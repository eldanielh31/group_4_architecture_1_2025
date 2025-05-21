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
# Convierte una lista de tuplas (v0, v1) de vuelta a texto plano
# ------------------------------------------
def blocks_to_str(blocks):
    result = b""
    for v0, v1 in blocks:
        result += v0.to_bytes(4, "big") + v1.to_bytes(4, "big")
    return result.rstrip(b"\x00").decode("utf-8", errors="ignore")

# ------------------------------------------
# 1. Leer archivo de texto de entrada (test.txt)
# ------------------------------------------
with open("test.txt", "r") as f:
    content = f.read()

# 2. Convertir el texto en bloques de 64 bits (v0, v1)
text_blocks = str_to_blocks(content)

# 3. Leer el archivo de ensamblador externo (program.asm)
with open("program.asm", "r") as f:
    program_src = f.readlines()  # Cada línea es una instrucción ensamblador

# Lista para almacenar los bloques descifrados
recovered_blocks = []

# ------------------------------------------
# 4. Procesar cada bloque de texto por separado
# ------------------------------------------
for i, (v0, v1) in enumerate(text_blocks):
    print(f"\n[ Bloque {i} ] ------------------")

    # Cargar el bloque actual (v0, v1) en memoria
    cpu.data_memory[0] = v0
    cpu.data_memory[1] = v1

    # Reiniciar el procesador para cada bloque
    cpu.reset() #IMPORTANTE para que no se quede en HALT

    # Ensamblar el programa y cargarlo en memoria de instrucciones
    program = assemble(program_src)
    cpu.load_program(program)

    # Ejecutar el programa (cifrado + descifrado)
    cpu.run()

    # Leer resultado del descifrado desde la memoria (posición 20 y 21)
    plain_v0 = cpu.data_memory[20]
    plain_v1 = cpu.data_memory[21]
    recovered_blocks.append((plain_v0, plain_v1))

# 5. Reconstruir el texto a partir de los bloques descifrados
recovered = blocks_to_str(recovered_blocks)

# 6. Guardar el resultado final en un archivo (output.txt)
with open("output.txt", "w") as f:
    f.write(recovered)

# 7. Imprimir el resultado en consola
print("\nTexto original recuperado:")
print(recovered)
