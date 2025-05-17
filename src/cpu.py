
from isa import ISA

registers = [0] * 16
data_memory = [0] * 1024
instr_memory = []
vault = {0: [0]*4, 1: [0]*4, 2: [0]*4, 3: [0]*4}
pc = 1
halted = False

def load_program(program):
    global instr_memory
    instr_memory = program

def execute_instruction():
    global pc, halted
    instr = instr_memory[pc]
    opcode = instr[0]

    if opcode == ISA["LOADK"]:
        kid = instr[1]
        vault[kid] = [instr[2], instr[3], instr[4], instr[5]]
        pc += 1

    elif opcode == ISA["MOVB"]:
        base_addr = instr[1]
        registers[1] = int(data_memory[base_addr])
        registers[2] = int(data_memory[base_addr + 1])
        pc += 1

    elif opcode == ISA["STB"]:
        base_addr = instr[1]
        data_memory[base_addr] = registers[3]
        data_memory[base_addr + 1] = registers[4]
        pc += 1

    elif opcode == ISA["ENC32"]:
        kid = instr[1]
        delta = 0x9e3779b9
        sum_ = 0
        v0 = int(registers[1])
        v1 = int(registers[2])
        key = vault[kid]
        for _ in range(32):
            sum_ = (sum_ + delta) & 0xFFFFFFFF
            v0 = (v0 + (((v1 << 4) + key[0]) ^ (v1 + sum_) ^ ((v1 >> 5) + key[1]))) & 0xFFFFFFFF
            v1 = (v1 + (((v0 << 4) + key[2]) ^ (v0 + sum_) ^ ((v0 >> 5) + key[3]))) & 0xFFFFFFFF
        registers[3], registers[4] = v0, v1
        pc += 1

    elif opcode == ISA["DEC32"]:
        kid = instr[1]
        delta = 0x9e3779b9
        sum_ = (delta * 32) & 0xFFFFFFFF
        v0 = int(registers[1])
        v1 = int(registers[2])
        key = vault[kid]
        for _ in range(32):
            v1 = (v1 - (((v0 << 4) + key[2]) ^ (v0 + sum_) ^ ((v0 >> 5) + key[3]))) & 0xFFFFFFFF
            v0 = (v0 - (((v1 << 4) + key[0]) ^ (v1 + sum_) ^ ((v1 >> 5) + key[1]))) & 0xFFFFFFFF
            sum_ = (sum_ - delta) & 0xFFFFFFFF
        registers[3], registers[4] = v0, v1
        pc += 1

    elif opcode == ISA["HALT"]:
        halted = True

    else:
        raise Exception(f"Unknown opcode: {opcode}")

def run():
    while not halted:
        execute_instruction()
