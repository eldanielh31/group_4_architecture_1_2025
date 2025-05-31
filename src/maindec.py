from assembler import assemble
import cpu

# ------------------------------------------
# Bloques cifrados previamente generados (por ENC32)
# ------------------------------------------
bloques_cifrados = [
    (0xC46A65E9, 0xA2B41DFB),  # bloque 1
    (0x368481FC, 0xF7E36BF0)   # bloque 2
]

# Cargar los bloques cifrados en memoria desde Mem[20]
for i, (v0, v1) in enumerate(bloques_cifrados):
    cpu.data_memory[20 + i * 2] = v0
    cpu.data_memory[20 + i * 2 + 1] = v1

# ------------------------------------------
# Cargar y ensamblar programa de descifrado
# ------------------------------------------
with open("dec.asm") as f:
    source = f.readlines()
program = assemble(source)
cpu.load_program(program)

# ------------------------------------------
# Ejecutar el pipeline
# ------------------------------------------
cpu.run()

# ------------------------------------------
# Mostrar texto descifrado desde Mem[30–33]
# ------------------------------------------
result_bytes = b''
for i in range(30, 34):
    result_bytes += cpu.data_memory[i].to_bytes(4, 'big')

print("\nTexto descifrado:", result_bytes.decode('utf-8', errors='replace'))
