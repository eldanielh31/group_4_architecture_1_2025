from isa import ISA

# Estado del procesador
registers = [0] * 16
instr_memory = []
data_memory = [0] * 1024
vault = {0: [0]*4, 1: [0]*4, 2: [0]*4, 3: [0]*4}
halted = False

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


def fetch():
    global pc, IF_ID
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

        for i in range(len(args)):
            if isinstance(args[i], int) and 0 <= args[i] < len(registers):
                if EX_MEM.get('dest') == args[i]:
                    args[i] = EX_MEM.get('result') if not isinstance(EX_MEM.get('result'), tuple) else EX_MEM.get('result')[0]
                    print(f"[FWD] Forwarded from EX_MEM to argument {i}")
                elif MEM_WB.get('dest') == args[i]:
                    args[i] = MEM_WB.get('result') if not isinstance(MEM_WB.get('result'), tuple) else MEM_WB.get('result')[0]
                    print(f"[FWD] Forwarded from MEM_WB to argument {i}")

        ID_EX = {'opcode': opcode, 'args': args, 'instr': instr}
        print(f"[ID] Decoded instruction: opcode={opcode}, args={args}")
    else:
        ID_EX = {'opcode': None}


def execute():
    global ID_EX, EX_MEM
    opcode = ID_EX.get('opcode')
    args = ID_EX.get('args')
    EX_MEM = {'opcode': opcode, 'args': args, 'result': None}

    if opcode == ISA['ADD']:
        EX_MEM['result'] = registers[args[0]] + registers[args[1]]
        EX_MEM['dest'] = args[2]
    elif opcode == ISA['SUB']:
        EX_MEM['result'] = registers[args[0]] - registers[args[1]]
        EX_MEM['dest'] = args[2]
    elif opcode == ISA['XOR']:
        EX_MEM['result'] = registers[args[0]] ^ registers[args[1]]
        EX_MEM['dest'] = args[2]
    elif opcode == ISA['SHL']:
        EX_MEM['result'] = registers[args[0]] << args[1]
        EX_MEM['dest'] = args[0]
    elif opcode == ISA['SHR']:
        EX_MEM['result'] = registers[args[0]] >> args[1]
        EX_MEM['dest'] = args[0]
    elif opcode == ISA['ENC32']:
        kid = args[0]
        key = vault[kid]
        v0 = registers[1]
        v1 = registers[2]
        sum = 0
        delta = 0x9e3779b9
        for _ in range(32):
            sum = (sum + delta) & 0xFFFFFFFF
            v0 = (v0 + (((v1 << 4) + key[0]) ^ (v1 + sum) ^ ((v1 >> 5) + key[1]))) & 0xFFFFFFFF
            v1 = (v1 + (((v0 << 4) + key[2]) ^ (v0 + sum) ^ ((v0 >> 5) + key[3]))) & 0xFFFFFFFF
        EX_MEM['result'] = (v0, v1)
        EX_MEM['dest'] = (3, 4)
        print(f"[EX] ENC32 result: v0={v0}, v1={v1}")
    elif opcode == ISA['DEC32']:
        kid = args[0]
        key = vault[kid]
        v0 = registers[1]
        v1 = registers[2]
        delta = 0x9e3779b9
        sum = (delta * 32) & 0xFFFFFFFF
        for _ in range(32):
            v1 = (v1 - (((v0 << 4) + key[2]) ^ (v0 + sum) ^ ((v0 >> 5) + key[3]))) & 0xFFFFFFFF
            v0 = (v0 - (((v1 << 4) + key[0]) ^ (v1 + sum) ^ ((v1 >> 5) + key[1]))) & 0xFFFFFFFF
            sum = (sum - delta) & 0xFFFFFFFF
        EX_MEM['result'] = (v0, v1)
        EX_MEM['dest'] = (3, 4)
        print(f"[EX] DEC32 result: v0={v0}, v1={v1}")
    elif opcode == ISA['MOVB']:
        addr = args[0]
        registers[1] = data_memory[addr]
        registers[2] = data_memory[addr + 1]
        print(f"[EX] MOVB loaded R1 = {registers[1]:08X}, R2 = {registers[2]:08X} from Mem[{addr}] and Mem[{addr + 1}]")
    elif opcode == ISA['HALT']:
        EX_MEM['halt'] = True


def memory_access():
    global EX_MEM, MEM_WB
    opcode = EX_MEM.get('opcode')
    MEM_WB = {'opcode': opcode, 'result': EX_MEM.get('result'), 'dest': EX_MEM.get('dest')}

    if opcode == ISA['LD']:
        addr = EX_MEM['args'][1]
        MEM_WB['result'] = data_memory[addr]
        MEM_WB['dest'] = EX_MEM['args'][0]
    elif opcode == ISA['ST']:
        addr = EX_MEM['args'][1]
        data_memory[addr] = registers[EX_MEM['args'][0]]
    elif opcode == ISA['STB']:
        addr = EX_MEM['args'][0]
        data_memory[addr] = registers[3]
        data_memory[addr + 1] = registers[4]
        print(f"[MEM] STB -> Mem[{addr}] = {registers[3]:08X}, Mem[{addr+1}] = {registers[4]:08X}")


def write_back():
    global MEM_WB, halted
    if MEM_WB.get('opcode') == ISA['HALT'] or MEM_WB.get('halt'):
        halted = True
        print("[WB] HALT encountered. Stopping execution.")
        return

    dest = MEM_WB.get('dest')
    result = MEM_WB.get('result')
    if dest is not None:
        if isinstance(dest, tuple):
            registers[dest[0]] = result[0]
            registers[dest[1]] = result[1]
            print(f"[WB] Write to R{dest[0]} = {result[0]}, R{dest[1]} = {result[1]}")
        else:
            registers[dest] = result
            print(f"[WB] Write to R{dest} = {result}")


def step():
    global cycle_count
    print(f"\n========== Cycle {cycle_count} ==========")
    write_back()
    memory_access()
    execute()
    decode()
    fetch()
    print_cpu_state()
    cycle_count += 1


def run():
    global halted
    while not halted:
        step()
