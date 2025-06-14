from isa import ISA
import time

# Registros, memorias y PC
registers      = [0] * 16
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
result = 0
dest = 0
op1 = 0
op2 = 0

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
    global pc, halted, instruction_count, cycle_count, result, dest, op1, op2

    instr = instr_memory[pc]
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
        data_memory[base_addr] = crypto_registers["C0"]
        data_memory[base_addr + 1] = crypto_registers["C1"]
        print(f" -> STB saved C0={hex(crypto_registers["C0"])}, C1={hex(crypto_registers["C1"])}")

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

    elif opcode == ISA['MOV']:
        dest = instr[1] 
        result = instr[2]
        registers[dest] = registers[result]
        pc += 1
    elif opcode == ISA['ADD']:
        dest = instr[3]
        op1 = instr[1]
        op2 = instr[2]
        result = registers[op1] + registers[op2]
        registers[dest] = result 
        pc += 1
    elif opcode == ISA['SUB']:
        dest = instr[3]
        op1 = instr[1]
        op2 = instr[2]
        result = registers[op1] - registers[op2]
        registers[dest] = result 
        pc += 1
    elif opcode == ISA['SHR']:
        dest = instr[3]
        op1 = instr[1]
        op2 = instr[2]
        result = registers[op1] >> registers[op2]
        registers[dest] = result 
        pc += 1
    elif opcode == ISA['SHL']:
        # instr should be a 4‑tuple/list: (opcode, op1, op2, dest)
        # let’s unpack and inspect
        _, raw_op1, raw_op2, raw_dest = instr
      

        # now make sure they’re ints (or map register names to ints here)
        op1  = int(raw_op1)
        op2  = int(raw_op2)
        dest = int(raw_dest)

        result = registers[op1] << registers[op2]
        registers[dest] = result
        pc += 1
    elif opcode == ISA['XOR']:
        dest = instr[3]
        op1 = instr[1]
        op2 = instr[2]
        result = registers[op1] ^ registers[op2]
        registers[dest] = result 
        pc += 1
    elif opcode == ISA['ST']:
        dest = instr[2]
        result = instr[1]
        data_memory[dest] = registers[result]  
        pc += 1
    elif opcode == ISA['LD']:
        dest = instr[1]
        result = instr[2]
        registers[dest] = data_memory[result]  
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

    ips = instruction_count / elapsed_time
    mips = ips / 1e6
    ipc = instruction_count / cycle_count if cycle_count > 0 else float('nan')

    print(f"[Uniciclo] Throughput: {ips:.2f} instr/s ({mips:.2f} MIPS)")
    print(f"[Uniciclo] IPC promedio: {ipc:.2f} instr/ciclo")
