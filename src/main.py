from assembler import assemble
import cpu

# ------------------------------------------
# Función para dividir texto plano en bloques de 64 bits (8 bytes)
# Devuelve una lista de tuplas (v0, v1) donde cada valor es de 32 bits
# ------------------------------------------
def str_to_blocks(text):
    data = text.encode("utf-8")  # Convierte el texto a bytes
    blocks = []
    for i in range(0, len(data), 8):
        chunk = data[i:i+8].ljust(8, b"\x00")  # Asegura que cada bloque tenga 8 bytes
        v0 = int.from_bytes(chunk[:4], "big")  # Primeras 4 bytes como entero (v0)
        v1 = int.from_bytes(chunk[4:], "big")  # Siguientes 4 bytes como entero (v1)
        blocks.append((v0, v1))
    return blocks


# ------------------------------------------
# Preparar memoria para cifrado de texto
# ------------------------------------------
texto_original = "Hola mundo"
bloques = str_to_blocks(texto_original)

for i, (v0, v1) in enumerate(bloques):  
    cpu.data_memory[i * 2] = v0
    cpu.data_memory[i * 2 + 1] = v1

# ------------------------------------------
# Cargar y ensamblar el programa
# ------------------------------------------
with open("program.asm") as f:
    source = f.readlines()
program = assemble(source)
cpu.load_program(program)

# ------------------------------------------
# Ejecutar el programa con CPU en pipeline
# ------------------------------------------
cpu.run()

# ------------------------------------------
# Mostrar resultados en consola
# ------------------------------------------
print("\nMemoria final:")
for i in range(0, 24, 2):
    v0 = cpu.data_memory[i]
    v1 = cpu.data_memory[i+1]
    print(f"Mem[{i:02}] = {v0:08X}, Mem[{i+1:02}] = {v1:08X}")
    
# Mostrar texto completo descifrado desde Mem[20] hasta Mem[23]
result_bytes = b''
for i in range(20, 24):
    result_bytes += cpu.data_memory[i].to_bytes(4, 'big')

print("Texto desencriptado:", result_bytes.decode('utf-8', errors='replace'))

