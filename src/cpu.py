from isa import ISA

# Estado del procesador
registers = [0] * 16
data_memory = [0] * 1024
instr_memory = []
vault = {0: [0]*4, 1: [0]*4, 2: [0]*4, 3: [0]*4}
cycles = 0
instructions = 0

# Registros internos del multiciclo
pc = 0
ir = None           # Instruction Register
state = "FETCH"     # Estado actual de la máquina de estados
halted = False

# Variables temporales para instrucciones complejas
tmp = {
    "opcode": None,
    "args": None,
    "v0": None,
    "v1": None,
    "sum": None,
    "rounds": 0,
    "key": None,
    "mode": None,  # "ENC" o "DEC"
}

def load_program(program):
    global instr_memory
    instr_memory = program

def step():
    global pc, halted, state, ir, tmp, cycles, instructions 
    cycles += 1

    if state == "FETCH":
        if pc >= len(instr_memory):
            halted = True
            return
        ir = instr_memory[pc]
        tmp["opcode"] = ir[0]
        tmp["args"] = ir[1:]
        state = "DECODE"

    elif state == "DECODE":
        opcode = tmp["opcode"]

        if opcode == ISA["LOADK"]:
            kid, *key_parts = tmp["args"]
            vault[kid] = key_parts
            pc += 1
            instructions += 1
            state = "FETCH"

        elif opcode == ISA["MOVB"]:
            tmp["addr"] = tmp["args"][0]
            state = "EXEC_MOVB"

        elif opcode == ISA["STB"]:
            tmp["addr"] = tmp["args"][0]
            state = "EXEC_STB"

        elif opcode == ISA["ENC32"]:
            kid = tmp["args"][0]
            tmp["key"] = vault[kid]
            tmp["sum"] = 0
            tmp["rounds"] = 0
            tmp["v0"] = registers[1]
            tmp["v1"] = registers[2]
            tmp["mode"] = "ENC"
            print(f" -> ENC32 START: v0={hex(tmp['v0'])}, v1={hex(tmp['v1'])}")
            state = "ENC_LOOP"

        elif opcode == ISA["DEC32"]:
            kid = tmp["args"][0]
            tmp["key"] = vault[kid]
            tmp["sum"] = (0x9e3779b9 * 32) & 0xFFFFFFFF
            tmp["rounds"] = 0
            tmp["v0"] = registers[1]
            tmp["v1"] = registers[2]
            tmp["mode"] = "DEC"
            print(f" -> DEC32 START: v0={hex(tmp['v0'])}, v1={hex(tmp['v1'])}")
            state = "ENC_LOOP"

        elif opcode == ISA["HALT"]:
            print(" -> HALT encountered")
            halted = True

    elif state == "EXEC_MOVB":
        addr = tmp["addr"]
        registers[1] = int(data_memory[addr])
        registers[2] = int(data_memory[addr + 1])
        print(f" -> MOVB loaded R1={hex(registers[1])}, R2={hex(registers[2])}")
        pc += 1
        instructions += 1
        state = "FETCH"

    elif state == "EXEC_STB":
        addr = tmp["addr"]
        data_memory[addr] = registers[3]
        data_memory[addr + 1] = registers[4]
        print(f" -> STB saved R3={hex(registers[3])}, R4={hex(registers[4])}")
        pc += 1
        instructions += 1
        state = "FETCH"

    elif state == "ENC_LOOP":
        delta = 0x9e3779b9
        v0 = tmp["v0"]
        v1 = tmp["v1"]
        key = tmp["key"]
        sum_ = tmp["sum"]

        if tmp["mode"] == "ENC":
            sum_ = (sum_ + delta) & 0xFFFFFFFF
            v0 = (v0 + (((v1 << 4) + key[0]) ^ (v1 + sum_) ^ ((v1 >> 5) + key[1]))) & 0xFFFFFFFF
            v1 = (v1 + (((v0 << 4) + key[2]) ^ (v0 + sum_) ^ ((v0 >> 5) + key[3]))) & 0xFFFFFFFF
            tmp["sum"] = sum_
        else:  # DEC
            v1 = (v1 - (((v0 << 4) + key[2]) ^ (v0 + sum_) ^ ((v0 >> 5) + key[3]))) & 0xFFFFFFFF
            v0 = (v0 - (((v1 << 4) + key[0]) ^ (v1 + sum_) ^ ((v1 >> 5) + key[1]))) & 0xFFFFFFFF
            tmp["sum"] = (sum_ - delta) & 0xFFFFFFFF

        tmp["v0"] = v0
        tmp["v1"] = v1
        tmp["rounds"] += 1

        if tmp["rounds"] >= 32:
            registers[3] = v0
            registers[4] = v1
            label = "ENC32" if tmp["mode"] == "ENC" else "DEC32"
            print(f" -> {label} END: R3={hex(v0)}, R4={hex(v1)}")
            pc += 1
            instructions += 1
            state = "FETCH"

def reset():
    global pc, halted, state, ir, tmp, cycles, instructions
    pc = 0
    halted = False
    state = "FETCH"
    ir = None
    cycles = 0
    instructions = 0
    tmp = {
        "opcode": None,
        "args": None,
        "v0": None,
        "v1": None,
        "sum": None,
        "rounds": 0,
        "key": None,
        "mode": None,
    }

# Ejecuta el procesador hasta que se detenga
def run():
    while not halted:
        step()
    print(f" -> Total cycles: {cycles}")
    print(f" -> Total instructions: {instructions}")
    if instructions > 0:
        cpi = cycles / instructions
        print(f" -> CPI: {cpi:.2f}")

