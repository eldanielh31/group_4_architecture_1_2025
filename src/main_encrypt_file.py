from assembler import assemble
import cpu
import sys
import hashlib

def str_to_blocks(data_bytes):
    blocks = []
    for i in range(0, len(data_bytes), 8):
        chunk = data_bytes[i:i+8].ljust(8, b"\x00")
        v0 = int.from_bytes(chunk[:4], "big")
        v1 = int.from_bytes(chunk[4:], "big")
        blocks.append((v0, v1))
    return blocks

def load_blocks_into_memory(blocks):
    for i, (v0, v1) in enumerate(blocks):
        cpu.data_memory[i * 2] = v0
        cpu.data_memory[i * 2 + 1] = v1

def dump_memory_blocks(n_blocks, offset=10):
    result = b''
    for i in range(n_blocks):
        v0 = cpu.data_memory[offset + i * 2]
        v1 = cpu.data_memory[offset + i * 2 + 1]
        result += v0.to_bytes(4, 'big') + v1.to_bytes(4, 'big')
    return result

if len(sys.argv) < 3:
    print("Uso: python3 main_encrypt_file.py input.txt output.enc")
    sys.exit(1)

input_path = sys.argv[1]
output_path = sys.argv[2]

# Leer archivo a cifrar
with open(input_path, 'rb') as f:
    data = f.read()

blocks = str_to_blocks(data)
load_blocks_into_memory(blocks)

# Cargar programa
with open("program_enc.asm") as f:
    source = f.readlines()

program = assemble(source)
cpu.load_program(program)

# Cargar clave en bóveda
cpu.vault[0] = [0xA1B2C3D4, 0x11223344, 0x55667788, 0x99AABBCC]

# Ejecutar cifrado
cpu.run()

# Guardar salida cifrada
cipher_data = dump_memory_blocks(len(blocks))
with open(output_path, 'wb') as f:
    f.write(cipher_data)

print(f"Cifrado completado. MD5: {hashlib.md5(cipher_data).hexdigest()}")
