from isa import ISA
import time

# Estado del procesador
registers = [0] * 16
data_memory = [0] * 50000
instr_memory = []
vault = {0: [0]*4, 1: [0]*4, 2: [0]*4, 3: [0]*4}
# Registros dedicados para cifrado
crypto_registers = {
    "V0": 0,  # Entrada 1
    "V1": 0,  # Entrada 2
    "C0": 0,  # Salida 1
    "C1": 0   # Salida 2
}
cycles = 0
instructions = 0
elapsed_time = 0

# Contadores
default_cycles = 0
default_instructions = 0
cycles = default_cycles
instructions = default_instructions

# Registros internos del multiciclo
default_pc = 0
default_ir = None
default_state = "FETCH"
default_halted = False
pc = default_pc
ir = default_ir
state = default_state
halted = default_halted

# Variables temporales para instrucciones complejas
default_tmp = {
    "opcode": None,
    "args": None,
    "v0": None,
    "v1": None,
    "sum": None,
    "rounds": 0,
    "key": None,
    "mode": None,
}
tmp = default_tmp.copy()

def load_program(program):
    global instr_memory
    instr_memory = program.copy()

def step():
    global pc, halted, state, ir, tmp, cycles, instructions
    cycles += 1

    if state == "FETCH":
        if pc >= len(instr_memory):
            halted = True
            return
        ir = instr_memory[pc]
        print(ir)
        tmp["opcode"] = ir[0]
        tmp["args"] = ir[1:]
        state = "DECODE"

    elif state == "DECODE":
        opcode = tmp["opcode"]

        if opcode == ISA["LOADK"]:
            kid, *parts = tmp["args"]
            vault[kid] = parts.copy()
            pc += 1
            instructions += 1
            state = "FETCH"

        elif opcode == ISA["MOVB"]:
            tmp["addr"] = tmp["args"][0]
            state = "EXEC_MOVB"

        elif opcode == ISA["STB"]:
            tmp["addr"] = tmp["args"][0]
            state = "EXEC_STB"

        elif opcode in (ISA["ENC32"], ISA["DEC32"]):
            kid = tmp["args"][0]
            tmp["key"] = vault[kid].copy()
            if opcode == ISA["ENC32"]:
                tmp["sum"] = 0
                tmp["mode"] = "ENC"
            else:
                tmp["sum"] = (0x9e3779b9 * 32) & 0xFFFFFFFF
                tmp["mode"] = "DEC"
            tmp["rounds"] = 0
            tmp["v0"] = crypto_registers["V0"]
            tmp["v1"] = crypto_registers["V1"]
            state = "ENC_LOOP"

        elif opcode == ISA["HALT"]:
            halted = True
            state = "HALT"

    elif state == "EXEC_MOVB":
        addr = tmp["addr"]
        crypto_registers["V0"] = int(data_memory[addr])
        crypto_registers["V1"] = int(data_memory[addr + 1])
        pc += 1
        instructions += 1
        print(f" -> MOVB loaded V0={hex(crypto_registers['V0'])}, V1={hex(crypto_registers['V1'])}")
        state = "FETCH"

    elif state == "EXEC_STB":
        addr = tmp["addr"]
        data_memory[addr] = crypto_registers["C0"]
        data_memory[addr + 1] = crypto_registers["C1"]
        pc += 1
        instructions += 1
        print(f" -> STB saved C0={hex(c0)}, C1={hex(c1)}")

        # Limpieza segura de los registros
        for k in crypto_registers:
            crypto_registers[k] = 0
        print(" -> Crypto registers securely cleared")
        state = "FETCH"

    elif state == "ENC_LOOP":
        delta = 0x9e3779b9
        v0 = tmp["v0"]
        v1 = tmp["v1"]
        key = tmp["key"]
        sum_ = tmp["sum"]
        if tmp["mode"] == "ENC":
            print(f"ENC32 START: V0={hex(v0)}, V1={hex(v1)}")
            sum_ = (sum_ + delta) & 0xFFFFFFFF
            v0 = (v0 + (((v1 << 4) + key[0]) ^ (v1 + sum_) ^ ((v1 >> 5) + key[1]))) & 0xFFFFFFFF
            v1 = (v1 + (((v0 << 4) + key[2]) ^ (v0 + sum_) ^ ((v0 >> 5) + key[3]))) & 0xFFFFFFFF
        else:
            print(f"DEC32 START: V0={hex(v0)}, V1={hex(v1)}")
            v1 = (v1 - (((v0 << 4) + key[2]) ^ (v0 + sum_) ^ ((v0 >> 5) + key[3]))) & 0xFFFFFFFF
            v0 = (v0 - (((v1 << 4) + key[0]) ^ (v1 + sum_) ^ ((v1 >> 5) + key[1]))) & 0xFFFFFFFF
            sum_ = (sum_ - delta) & 0xFFFFFFFF

        tmp["sum"] = sum_
        tmp["v0"] = v0
        tmp["v1"] = v1
        tmp["rounds"] += 1

        if tmp["rounds"] >= 32:
            registers[3] = v0
            registers[4] = v1
            pc += 1
            instructions += 1
            state = "FETCH"

    # Otras fases podrían añadirse aquí para un multiciclo más detallado


def reset():
    global registers, data_memory, instr_memory, vault
    global pc, ir, state, halted, cycles, instructions, tmp
    registers = default_registers.copy()
    data_memory = default_data_memory.copy()
    instr_memory = default_instr_memory.copy()
    vault = {k: v.copy() for k, v in default_vault.items()}
    pc = default_pc
    ir = default_ir
    state = default_state
    halted = default_halted
    cycles = default_cycles
    instructions = default_instructions
    tmp = default_tmp.copy()

# Ejecución completa y medición de tiempo real
def run():
    global start_time, end_time, instruction_count, cycle_count, elapsed_time
    start_time = time.perf_counter()

    while not halted:
        step()

    end_time = time.perf_counter()
    elapsed = end_time - start_time

    elapsed_time = elapsed
    cycle_count = cycles
    instruction_count = instructions

    print(f"[Multiciclo] Instrucciones ejecutadas: {instruction_count}")
    print(f"[Multiciclo] Ciclos consumidos:       {cycle_count}")
    print(f"[Multiciclo] Tiempo de ejecución:     {elapsed:.6f} segundos")

