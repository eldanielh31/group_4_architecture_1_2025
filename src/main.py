from assembler import assemble
import cpu

# ------------------------------------------
# Función para dividir texto en bloques de 64 bits (8 bytes)
# ------------------------------------------
def str_to_blocks(text):
    data = text.encode("utf-8")
    blocks = []
    for i in range(0, len(data), 8):
        chunk = data[i:i+8].ljust(8, b"\x00")
        v0 = int.from_bytes(chunk[:4], "big")
        v1 = int.from_bytes(chunk[4:], "big")
        blocks.append((v0, v1))
    return blocks

# ------------------------------------------
# Función para convertir bloques de enteros a texto
# ------------------------------------------
def blocks_to_str(blocks):
    result_bytes = b''
    for v0, v1 in blocks:
        result_bytes += v0.to_bytes(4, 'big') + v1.to_bytes(4, 'big')
    return result_bytes.rstrip(b'\x00').decode('utf-8', errors='replace')

# ------------------------------------------
# Entrada de texto a cifrar
# ------------------------------------------
texto_original = "Hola Daniel Brenes"
bloques = str_to_blocks(texto_original)

# Guardamos los bloques en memoria (usamos desde la dirección 0)
for i, (v0, v1) in enumerate(bloques):
    cpu.data_memory[i * 2] = v0
    cpu.data_memory[i * 2 + 1] = v1

# ------------------------------------------
# Ensamblar y cargar el programa
# ------------------------------------------
with open("test.asm") as f:
    source = f.readlines()
program = assemble(source)
cpu.load_program(program)

# ------------------------------------------
# Ejecutar el programa
# ------------------------------------------
cpu.run()

# ------------------------------------------
# Leer bloques desencriptados desde Mem[20...]
# ------------------------------------------
dec_blocks = []
for i in range(len(bloques)):
    v0 = cpu.data_memory[20 + i * 2]
    v1 = cpu.data_memory[20 + i * 2 + 1]
    dec_blocks.append((v0, v1))

texto_desencriptado = blocks_to_str(dec_blocks)

# ------------------------------------------
# Imprimir resultados
# ------------------------------------------
print("\nTexto original:", texto_original)
print("Texto desencriptado:", texto_desencriptado)
