from isa import ISA

# Estado del procesador
registers = [0] * 16
instr_memory = []
data_memory = [0] * 1024
vault = {0: [0]*4, 1: [0]*4, 2: [0]*4, 3: [0]*4}
halted = False
#TODO: Agregar registros temporales privados para manejar las encriptaciones dentro de las instrucciones

# Registros inter-etapas del pipeline
IF_ID = {}
ID_EX = {}
EX_MEM = {}
MEM_WB = {}

pc = 0
cycle_count = 0

def load_program(program):
    global instr_memory
    instr_memory = program

def print_cpu_state():
    print("\n--- CPU STATE ---")
    print(f"PC: {pc}")
    print(f"Registers: {[f'R{i}={r:08X}' for i, r in enumerate(registers)]}")
    print(f"Vault: {vault}")
    print("---------------\n")

def print_pipeline_registers():
    print("--- Pipeline Registers ---")
    print(f"IF/ID:  {IF_ID}")
    print(f"ID/EX:  {ID_EX}")
    print(f"EX/MEM:{EX_MEM}")
    print(f"MEM/WB:{MEM_WB}")
    print("--------------------------\n")

def fetch():
    global pc, IF_ID
    if 'jumped' in EX_MEM:
        print(f"[IF] Skipped fetch due to jump")
        return
    if pc < len(instr_memory):
        IF_ID = {'instr': instr_memory[pc], 'pc': pc}
        print(f"[IF] Fetched instruction at PC={pc}: {instr_memory[pc]}")
        pc += 1
    else:
        IF_ID = {'instr': None}

def decode():
    global IF_ID, ID_EX, EX_MEM, MEM_WB
    instr = IF_ID.get('instr')
    if instr:
        opcode = instr[0]
        args = instr[1:]

        val_args = []
        for i, arg in enumerate(args):
            if isinstance(arg, tuple) and arg[0] == '#':
                val_args.append(arg[1])
            elif isinstance(arg, int) and 0 <= arg < len(registers):
                dest = EX_MEM.get('dest')
                if isinstance(dest, tuple) and arg in dest:
                    idx = dest.index(arg)
                    val_args.append(EX_MEM.get('result')[idx])
                    print(f"[FWD] Forwarded from EX_MEM to argument {i}")
                elif dest == arg:
                    val_args.append(EX_MEM.get('result'))
                    print(f"[FWD] Forwarded from EX_MEM to argument {i}")
                else:
                    dest = MEM_WB.get('dest')
                    if isinstance(dest, tuple) and arg in dest:
                        idx = dest.index(arg)
                        val_args.append(MEM_WB.get('result')[idx])
                        print(f"[FWD] Forwarded from MEM_WB to argument {i}")
                    elif dest == arg:
                        val_args.append(MEM_WB.get('result'))
                        print(f"[FWD] Forwarded from MEM_WB to argument {i}")
                    else:
                        val_args.append(registers[arg])
            else:
                val_args.append(arg)

        ID_EX = {'opcode': opcode, 'args': args, 'val_args': val_args}
        print(f"[ID] Decoded instruction: opcode={opcode}, args={args}, val_args={val_args}")
    else:
        ID_EX = {'opcode': None}

def execute():
    global ID_EX, EX_MEM, pc
    opcode = ID_EX.get('opcode')
    args = ID_EX.get('args')
    val_args = ID_EX.get('val_args')

    EX_MEM.clear()
    EX_MEM.update({'opcode': opcode, 'args': args, 'result': None})

    print(f"[EX] Executing opcode={opcode}, args={args}, val_args={val_args}")
    if opcode is None:
        return

    elif opcode == ISA['MOV']:
        EX_MEM['result'] = val_args[1]
        EX_MEM['dest'] = args[0]
        print(f"[EX] MOV R{args[0]} = {val_args[1]}")

    elif opcode == ISA['ADD']:
        EX_MEM['result'] = val_args[0] + val_args[1]
        EX_MEM['dest'] = args[2]
        print(f"[EX] ADD R{args[2]} = {val_args[0]} + {val_args[1]}")

    elif opcode == ISA['SUB']:
        EX_MEM['result'] = val_args[0] - val_args[1]
        EX_MEM['dest'] = args[2]
        print(f"[EX] SUB R{args[2]} = {val_args[0]} - {val_args[1]}")

    elif opcode == ISA['SHR']:
        EX_MEM['result'] = val_args[0] >> val_args[1]
        EX_MEM['dest'] = args[2]
        print(f"[EX] SHR R{args[2]} = {val_args[0]} >> {val_args[1]}")

    elif opcode == ISA['SHL']:
        EX_MEM['result'] = val_args[0] << val_args[1]
        EX_MEM['dest'] = args[2]
        print(f"[EX] SHL R{args[2]} = {val_args[0]} << {val_args[1]}")

    elif opcode == ISA['XOR']:
        EX_MEM['result'] = val_args[0] ^ val_args[1]
        EX_MEM['dest'] = args[2]
        print(f"[EX] XOR R{args[2]} = {val_args[0]} ^ {val_args[1]}")

    elif opcode == ISA['ST']:
        addr = val_args[1] if isinstance(args[1], tuple) else args[1]
        data_memory[addr] = registers[args[0]]
        print(f"[EX] ST Mem[{addr}] = R{args[0]} = {registers[args[0]]}")

    elif opcode == ISA['LD']:
        addr = val_args[1] if isinstance(args[1], tuple) else args[1]
        EX_MEM['result'] = data_memory[addr]
        EX_MEM['dest'] = args[0]
        print(f"[EX] LD R{args[0]} = Mem[{addr}] = {data_memory[addr]}")

    elif opcode == ISA['MOVB']:
        addr = val_args[0] if isinstance(val_args[0], int) else 0
        if addr < 0 or addr + 1 >= len(data_memory):
            print(f"[EX] MOVB error: invalid memory address {addr}")
            EX_MEM['halt'] = True
            return
        registers[1] = data_memory[addr]
        registers[2] = data_memory[addr + 1]
        print(f"[EX] MOVB loaded R1 = {registers[1]:08X}, R2 = {registers[2]:08X} from Mem[{addr}] and Mem[{addr + 1}]")

    elif opcode == ISA['STB']:
        addr = val_args[0]
        data_memory[addr] = registers[3]
        data_memory[addr + 1] = registers[4]
        print(f"[EX] STB -> Mem[{addr}] = {registers[3]:08X}, Mem[{addr+1}] = {registers[4]:08X}")

    elif opcode == ISA['LOADK']:
        kid = args[0]
        if 0 <= kid <= 3:
            vault[kid] = args[1:5]
            print(f"[EX] LOADK -> Vault[{kid}] = {[f'{v:08X}' for v in vault[kid]]}")
        else:
            print(f"[EX] LOADK failed: invalid vault id {kid}")

    elif opcode == ISA['JMP']:
        pc = args[0]
        IF_ID.clear()
        ID_EX.clear()
        EX_MEM.clear()
        EX_MEM['jumped'] = True
        print(f"[EX] JMP to PC = {pc}")

    elif opcode == ISA['BEQ']:
        val1 = val_args[0]
        val2 = val_args[1]
        if val1 == val2:
            pc = args[2]
            IF_ID.clear()
            ID_EX.clear()
            EX_MEM.clear()
            EX_MEM['jumped'] = True
            print(f"[EX] BEQ taken: R{args[0]} == R{args[1]} -> PC = {pc}")
        else:
            print(f"[EX] BEQ not taken: R{args[0]} = {val1}, R{args[1]} = {val2}")

    elif opcode == ISA['BNE']:
        if registers[args[0]] != registers[args[1]]:
            pc = args[2]
            IF_ID.clear()
            ID_EX.clear()
            EX_MEM.clear()
            EX_MEM['jumped'] = True
            print(f"[EX] BNE taken to PC = {pc}")
        else:
            print(f"[EX] BNE not taken: R{args[0]} == R{args[1]}")

    elif opcode == ISA['HALT']:
        EX_MEM['halt'] = True
        print("[EX] HALT encountered")

    elif opcode == ISA['NOP']:
        print("[EX] NOP (no operation)")

def memory_access():
    global MEM_WB
    MEM_WB.clear()
    MEM_WB.update(EX_MEM)

def write_back():
    global halted
    if MEM_WB.get('opcode') == ISA['HALT'] or MEM_WB.get('halt'):
        halted = True
        print("[WB] HALT encountered. Stopping execution.")
        return

    dest = MEM_WB.get('dest')
    result = MEM_WB.get('result')

    if dest is not None:
        if isinstance(dest, tuple) and isinstance(result, tuple):
            for i, reg in enumerate(dest):
                registers[reg] = result[i]
                print(f"[WB] Write to R{reg} = {result[i]:08X}")
        else:
            registers[dest] = result
            print(f"[WB] Write to R{dest} = {result:08X}")

def step():
    global cycle_count
    print(f"\n========== Cycle {cycle_count} ==========")
    write_back()
    memory_access()
    execute()
    decode()
    fetch()
    print_cpu_state()
    print_pipeline_registers()
    cycle_count += 1

def run():
    global halted
    while not halted:
        step()
