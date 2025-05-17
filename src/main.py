from cpu import load_program, run, data_memory, registers
from assembler import assemble

def str_to_blocks(text):
    data = text.encode("utf-8")
    blocks = []
    for i in range(0, len(data), 8):
        chunk = data[i:i+8].ljust(8, b"\x00")
        v0 = int.from_bytes(chunk[:4], "big")
        v1 = int.from_bytes(chunk[4:], "big")
        blocks.append((v0, v1))
    return blocks

def blocks_to_str(blocks):
    result = b""
    for v0, v1 in blocks:
        result += v0.to_bytes(4, "big") + v1.to_bytes(4, "big")
    return result.rstrip(b"\x00").decode("utf-8", errors="ignore")

# Leer archivo de texto de entrada
with open("test.txt", "r") as f:
    content = f.read()

text_blocks = str_to_blocks(content)

# Leer el ensamblador desde archivo externo
with open("program.asm", "r") as f:
    program_src = f.readlines()

# Ensamblar el programa leído
program = assemble(program_src)

# Usamos un solo bloque para prueba
v0, v1 = text_blocks[0]
data_memory[0] = v0
data_memory[1] = v1

# Ejecutar programa
load_program(program)
run()

# Leer salida descifrada
plain_v0 = data_memory[20]
plain_v1 = data_memory[21]
recovered = blocks_to_str([(plain_v0, plain_v1)])

# Escribir resultado en archivo
with open("output.txt", "w") as f:
    f.write(recovered)

print("Texto original recuperado:")
print(recovered)
