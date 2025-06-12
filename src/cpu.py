from isa import ISA

# Estado del procesador
registers = [0] * 16
instr_memory = []
# data_memory = [0] * 1024
data_memory = [0] * 50000
vault = {0: [0]*4, 1: [0]*4, 2: [0]*4, 3: [0]*4}
halted = False
# Registros dedicados para cifrado
crypto_registers = {
    "V0": 0,  # Entrada 1
    "V1": 0,  # Entrada 2
    "C0": 0,  # Salida 1
    "C1": 0   # Salida 2
}

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
    print(
    f'crypto_registers: V0=0x{crypto_registers["V0"]:08X}, '
    f'V1=0x{crypto_registers["V1"]:08X}, '
    f'C0=0x{crypto_registers["C0"]:08X}, '
    f'C1=0x{crypto_registers["C1"]:08X}'
    )
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
        crypto_registers["V0"] = data_memory[addr]
        crypto_registers["V1"] = data_memory[addr + 1]
        print(f" -> MOVB loaded V0={hex(crypto_registers['V0'])}, V1={hex(crypto_registers['V1'])}")

    elif opcode == ISA['STB']:
        addr = val_args[0]

        # Forwarding para C0 y C1 desde EX_MEM o MEM_WB si están disponibles
        c0 = crypto_registers["C0"]
        c1 = crypto_registers["C1"]

        if EX_MEM.get('dest') == ('C0', 'C1') and isinstance(EX_MEM.get('result'), tuple):
            c0, c1 = EX_MEM['result']
            print("[FWD] Forwarded from EX_MEM to STB")
        elif MEM_WB.get('dest') == ('C0', 'C1') and isinstance(MEM_WB.get('result'), tuple):
            c0, c1 = MEM_WB['result']
            print("[FWD] Forwarded from MEM_WB to STB")

        if addr < 0 or addr + 1 >= len(data_memory):
            print(f"[EX] STB error: invalid memory address {addr}")
            EX_MEM['halt'] = True
            return

        data_memory[addr] = c0
        data_memory[addr + 1] = c1
        print(f" -> STB saved C0={hex(c0)}, C1={hex(c1)}")

        # Limpieza segura de los registros
        for k in crypto_registers:
            crypto_registers[k] = 0
        print(" -> Crypto registers securely cleared")

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

    elif opcode == ISA['ENC32']:
        kid = args[0]
        delta = 0x9e3779b9
        sum_ = 0
        v0 = crypto_registers["V0"]
        v1 = crypto_registers["V1"]
        key = vault[kid]
        #print(f"[EX] ENC32 START: V0={ascii(v0)}, V1={ascii(v1)}")
        print(chr(v0 & 0x000000FF))
        print(chr((v0 & 0x0000FF00)>>8))
        print(chr((v0 & 0x00FF0000)>>16))
        print(chr((v0 & 0xFF000000)>>24))
        print("Xddddddddddddddddddddddddddddddddddddddddddddddddddddddd")
        print(chr(v1 & 0x000000FF))
        print(chr((v1 & 0x0000FF00)>>8))
        print(chr((v1 & 0x00FF0000)>>16))
        print(chr((v1 & 0xFF000000)>>24))


        

        for _ in range(32):
            sum_ = (sum_ + delta) & 0xFFFFFFFF
            v0 = (v0 + (((v1 << 4) + key[0]) ^ (v1 + sum_) ^ ((v1 >> 5) + key[1]))) & 0xFFFFFFFF
            v1 = (v1 + (((v0 << 4) + key[2]) ^ (v0 + sum_) ^ ((v0 >> 5) + key[3]))) & 0xFFFFFFFF

        EX_MEM['result'] = (v0, v1)
        EX_MEM['dest'] = ('C0', 'C1')  # Especificamos que van al crypto_registers
        print(f"[EX] ENC32 END: C0={hex(v0)}, C1={hex(v1)}")

    elif opcode == ISA['DEC32']:
        kid = args[0]
        delta = 0x9e3779b9
        sum_ = (delta * 32) & 0xFFFFFFFF
        v0 = crypto_registers["V0"]
        v1 = crypto_registers["V1"]
        key = vault[kid]
        print(f"[EX] DEC32 START: V0={hex(v0)}, V1={hex(v1)}")

        for _ in range(32):
            v1 = (v1 - (((v0 << 4) + key[2]) ^ (v0 + sum_) ^ ((v0 >> 5) + key[3]))) & 0xFFFFFFFF
            v0 = (v0 - (((v1 << 4) + key[0]) ^ (v1 + sum_) ^ ((v1 >> 5) + key[1]))) & 0xFFFFFFFF
            sum_ = (sum_ - delta) & 0xFFFFFFFF

        EX_MEM['result'] = (v0, v1)
        EX_MEM['dest'] = ('C0', 'C1')
        print(f"[EX] DEC32 END: C0={hex(v0)}, C1={hex(v1)}")


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
                if isinstance(reg, str) and reg in crypto_registers:
                    crypto_registers[reg] = result[i]
                    print(f"[WB] Write to {reg} = {result[i]:08X}")
                else:
                    registers[reg] = result[i]
                    print(f"[WB] Write to R{reg} = {result[i]:08X}")
        else:
            if isinstance(dest, str) and dest in crypto_registers:
                crypto_registers[dest] = result
                print(f"[WB] Write to {dest} = {result:08X}")
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

def reset():
    global registers, data_memory, crypto_registers, vault, pc, cycle_count, halted, IF_ID, ID_EX, EX_MEM, MEM_WB
    registers[:] = [0] * 16
    data_memory[:] = [0] * len(data_memory)
    for k in crypto_registers:
        crypto_registers[k] = 0
    for k in vault:
        vault[k] = [0] * 4
    pc = 0
    cycle_count = 0
    halted = False
    IF_ID.clear()
    ID_EX.clear()
    EX_MEM.clear()
    MEM_WB.clear()
