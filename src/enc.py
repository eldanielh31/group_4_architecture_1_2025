from assembler import assemble
from cpu import load_program, run, data_memory, registers
import hashlib

# Parámetros
DELTA = 0x9e3779b9
KEY_HEX = [0xDEADBEEF, 0xDEADBEEF, 0xDEADBEEF, 0xDEADBEEF]
INPUT_FILE = "jorge_luis.txt"
OUTPUT_FILE = "jorge_luis.txt.enc"

# 1. Leer archivo y convertirlo a bloques de 8 bytes (64 bits)
with open(INPUT_FILE, "rb") as f:
    raw_data = f.read()

# Padding para que el tamaño sea múltiplo de 8
while len(raw_data) % 8 != 0:
    raw_data += b'\x00'

# Cargar datos en memoria de entrada (desde dirección 0)
for i in range(0, len(raw_data), 4):
    word = int.from_bytes(raw_data[i:i+4], byteorder='big')
    data_memory[i // 4] = word

# 2. Generar programa ensamblador
lines = [
    f"LOADK K0, 0x{KEY_HEX[0]:08X}, 0x{KEY_HEX[1]:08X}, 0x{KEY_HEX[2]:08X}, 0x{KEY_HEX[3]:08X}",
    "MOV R3, #0",
    f"MOV R4, #{len(raw_data) // 4}",  # cantidad de palabras
    "loop:",
    "MOV R1, R3",
    "MOVB R1",
    "ENC32 K0",
    "ADD #100, R3, R2",  # guardar en dirección 100+
    "STB R2",
    "ADD R3, #2, R3",
    "BNE R3, R4, loop",
    "HALT"
]

# 3. Ensamblar y ejecutar
program = assemble(lines)
load_program(program)
run()

# 4. Extraer memoria cifrada desde dirección 100
encrypted_bytes = bytearray()
for i in range(100, 100 + (len(raw_data) // 4), 2):
    word1 = data_memory[i]
    word2 = data_memory[i + 1]
    encrypted_bytes += word1.to_bytes(4, byteorder='big')
    encrypted_bytes += word2.to_bytes(4, byteorder='big')

with open(OUTPUT_FILE, "wb") as f:
    f.write(encrypted_bytes)

# 5. Mostrar hash MD5
md5_hash = hashlib.md5(encrypted_bytes).hexdigest()
print(f"✅ Archivo cifrado guardado en '{OUTPUT_FILE}'")
print(f"🔐 Hash MD5: {md5_hash}")
