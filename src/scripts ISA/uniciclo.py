from isa import ISA
import time

# Registros, memorias y PC
default_registers = [0] * 16
registers      = default_registers.copy()
data_memory    = [0] * 50000
instr_memory   = []
vault          = {0: [0]*4, 1: [0]*4, 2: [0]*4, 3: [0]*4}
pc             = 0
halted         = False
# Registros dedicados para cifrado
crypto_registers = {
    "V0": 0,  # Entrada 1
    "V1": 0,  # Entrada 2
    "C0": 0,  # Salida 1
    "C1": 0   # Salida 2
}


# Contadores
default_instr_count = 0
default_cycle_count = 0
instruction_count = default_instr_count
cycle_count       = default_cycle_count

# Tiempo de ejecución
default_start_time = 0
default_end_time   = 0
start_time = default_start_time
end_time   = default_end_time
elapsed_time = 0

def load_program(program):
    global instr_memory, pc, halted, instruction_count, cycle_count, start_time, end_time
    instr_memory      = program
    pc                = 0
    halted            = False
    instruction_count = default_instr_count
    cycle_count       = default_cycle_count
    start_time        = default_start_time
    end_time          = default_end_time


def execute_instruction():
    global pc, halted, instruction_count, cycle_count

    instr = instr_memory[pc]
    print (instr)
    opcode = instr[0]
        

    # Cada instrucción uniciclo consume 1 ciclo
    instruction_count += 1
    cycle_count       += 1

    if opcode == ISA["LOADK"]:
        kid = instr[1]
        vault[kid] = [instr[2], instr[3], instr[4], instr[5]]
        pc += 1

    elif opcode == ISA["MOVB"]:
        base_addr = instr[1]
        crypto_registers["V0"] = data_memory[base_addr]
        crypto_registers["V1"] = data_memory[base_addr + 1]
        print(f" -> MOVB loaded V0={hex(crypto_registers['V0'])}, V1={hex(crypto_registers['V1'])}")
        pc += 1

    elif opcode == ISA["STB"]:
        base_addr = instr[1]
        data_memory[base_addr] = c0
        data_memory[base_addr + 1] = c1
        print(f" -> STB saved C0={hex(c0)}, C1={hex(c1)}")

        # Limpieza segura de los registros
        for k in crypto_registers:
            crypto_registers[k] = 0
        print(" -> Crypto registers securely cleared")
        pc += 1

    elif opcode == ISA["ENC32"]:
        kid   = instr[1]
        delta = 0x9e3779b9
        sum_  = 0
        v0    = crypto_registers["V0"]
        v1    = crypto_registers["V1"]
        key   = vault[kid]
        print(f"ENC32 START: V0={hex(v0)}, V1={hex(v1)}")
        for _ in range(32):
            sum_ = (sum_ + delta) & 0xFFFFFFFF
            v0   = (v0 + (((v1 << 4) + key[0]) ^ (v1 + sum_) ^ ((v1 >> 5) + key[1]))) & 0xFFFFFFFF
            v1   = (v1 + (((v0 << 4) + key[2]) ^ (v0 + sum_) ^ ((v0 >> 5) + key[3]))) & 0xFFFFFFFF
        registers[3], registers[4] = v0, v1
        pc += 1
        print(f"ENC32 END: V0={hex(v0)}, V1={hex(v1)}")

    elif opcode == ISA["DEC32"]:
        kid   = instr[1]
        delta = 0x9e3779b9
        sum_  = (delta * 32) & 0xFFFFFFFF
        v0    = crypto_registers["V0"]
        v1    = crypto_registers["V1"]
        key   = vault[kid]
        print(f"DEC32 START: V0={hex(v0)}, V1={hex(v1)}")
        for _ in range(32):
            v1   = (v1 - (((v0 << 4) + key[2]) ^ (v0 + sum_) ^ ((v0 >> 5) + key[3]))) & 0xFFFFFFFF
            v0   = (v0 - (((v1 << 4) + key[0]) ^ (v1 + sum_) ^ ((v1 >> 5) + key[1]))) & 0xFFFFFFFF
            sum_ = (sum_ - delta) & 0xFFFFFFFF
        crypto_registers["C0"],crypto_registers["C1"] = v0, v1
        print(f" DEC32 END: C0={hex(v0)}, C1={hex(v1)}")
        pc += 1

    elif opcode == ISA["HALT"]:
        halted = True

    else:
        raise Exception(f"Unknown opcode: {opcode}")


def run():
    global start_time, end_time, instruction_count, cycle_count, elapsed_time
    # Inicia medición de tiempo real
    start_time = time.perf_counter()

    while not halted:
        execute_instruction()

    # Termina medición
    end_time = time.perf_counter()
    elapsed = end_time - start_time

    # Guardar métricas en atributos del módulo
    elapsed_time = elapsed
    cycle_count = cycle_count
    instruction_count = instruction_count

    # Impresiones originales (pueden comentarse si no se desean duplicados)
    print(f"[Uniciclo] Instrucciones ejecutadas: {instruction_count}")
    print(f"[Uniciclo] Ciclos consumidos:       {cycle_count}")
    print(f"[Uniciclo] Tiempo de ejecución:     {elapsed:.6f} segundos")
