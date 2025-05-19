from isa import ISA  # Importa el set de instrucciones definido externamente

# ------------------------------------------
# Estado del procesador (simulado)
# ------------------------------------------

registers = [0] * 16  # Registros generales R0-R15 (solo se usan R1–R4 aquí)
data_memory = [0] * 1024  # Memoria de datos (espacio de lectura/escritura)
instr_memory = []  # Memoria de instrucciones cargadas (programa ensamblado)

# "Vault" o bóveda: almacena claves de 128 bits (4 palabras de 32 bits) para cifrado/descifrado
vault = {
    0: [0]*4,
    1: [0]*4,
    2: [0]*4,
    3: [0]*4
}

pc = 0         # Program Counter: índice de la instrucción actual
halted = False # Señal de detención del procesador (estado HALT)

# ------------------------------------------
# Carga el programa ensamblado en la memoria de instrucciones
# ------------------------------------------
def load_program(program):
    global instr_memory
    instr_memory = program

# ------------------------------------------
# Ejecuta una instrucción según el valor de pc
# ------------------------------------------
def execute_instruction():
    global pc, halted
    instr = instr_memory[pc]
    opcode = instr[0]  # Primer elemento es el código de operación (opcode)

    print(f"[PC={pc}] Executing: {instr}")  # Debug: mostrar instrucción actual

    # Instrucción: LOADK <key_id>, k0, k1, k2, k3
    # Carga una clave en la "vault" (bóveda) de claves
    if opcode == ISA["LOADK"]:
        kid = instr[1]  # ID de la clave (0–3)
        vault[kid] = [instr[2], instr[3], instr[4], instr[5]]
        pc += 1

    # Instrucción: MOVB <direccion>
    # Carga dos palabras (v0, v1) desde memoria en R1 y R2
    elif opcode == ISA["MOVB"]:
        base_addr = instr[1]
        registers[1] = int(data_memory[base_addr])
        registers[2] = int(data_memory[base_addr + 1])
        print(f" -> MOVB loaded R1={hex(registers[1])}, R2={hex(registers[2])}")
        pc += 1

    # Instrucción: STB <direccion>
    # Guarda R3 y R4 en memoria (salida de cifrado/descifrado)
    elif opcode == ISA["STB"]:
        base_addr = instr[1]
        data_memory[base_addr] = registers[3]
        data_memory[base_addr + 1] = registers[4]
        print(f" -> STB saved R3={hex(registers[3])}, R4={hex(registers[4])}")
        pc += 1

    # Instrucción: ENC32 <key_id>
    # Cifra 64 bits (R1 y R2) con la clave vault[key_id], resultado en R3 y R4
    elif opcode == ISA["ENC32"]:
        kid = instr[1]
        delta = 0x9e3779b9  # Constante mágica del algoritmo TEA
        sum_ = 0
        v0 = int(registers[1])
        v1 = int(registers[2])
        key = vault[kid]
        print(f" -> ENC32 START: v0={hex(v0)}, v1={hex(v1)}")
        for _ in range(32):  # 32 rondas del algoritmo TEA
            sum_ = (sum_ + delta) & 0xFFFFFFFF
            v0 = (v0 + (((v1 << 4) + key[0]) ^ (v1 + sum_) ^ ((v1 >> 5) + key[1]))) & 0xFFFFFFFF
            v1 = (v1 + (((v0 << 4) + key[2]) ^ (v0 + sum_) ^ ((v0 >> 5) + key[3]))) & 0xFFFFFFFF
        registers[3], registers[4] = v0, v1
        print(f" -> ENC32 END: R3={hex(v0)}, R4={hex(v1)}")
        pc += 1

    # Instrucción: DEC32 <key_id>
    # Descifra 64 bits (R1 y R2) con la clave vault[key_id], resultado en R3 y R4
    elif opcode == ISA["DEC32"]:
        kid = instr[1]
        delta = 0x9e3779b9
        sum_ = (delta * 32) & 0xFFFFFFFF
        v0 = int(registers[1])
        v1 = int(registers[2])
        key = vault[kid]
        print(f" -> DEC32 START: v0={hex(v0)}, v1={hex(v1)}")
        for _ in range(32):  # 32 rondas inversas de TEA
            v1 = (v1 - (((v0 << 4) + key[2]) ^ (v0 + sum_) ^ ((v0 >> 5) + key[3]))) & 0xFFFFFFFF
            v0 = (v0 - (((v1 << 4) + key[0]) ^ (v1 + sum_) ^ ((v1 >> 5) + key[1]))) & 0xFFFFFFFF
            sum_ = (sum_ - delta) & 0xFFFFFFFF
        registers[3], registers[4] = v0, v1
        print(f" -> DEC32 END: R3={hex(v0)}, R4={hex(v1)}")
        pc += 1

    # Instrucción: HALT
    # Detiene la ejecución
    elif opcode == ISA["HALT"]:
        print(" -> HALT encountered")
        halted = True

    # Instrucción no reconocida
    else:
        raise Exception(f"Unknown opcode: {opcode}")

# ------------------------------------------
# Bucle de ejecución del procesador
# ------------------------------------------
def run():
    while not halted:
        execute_instruction()
