
import time
import cpu
from assembler import assemble
from hashlib import md5

# ------------------------------------------
# Utilidades para conversión
# ------------------------------------------
def read_file_to_blocks(filename):
    with open(filename, "rb") as f:
        data = f.read()
    blocks = []
    for i in range(0, len(data), 8):
        chunk = data[i:i+8].ljust(8, b"\x00")
        v0 = int.from_bytes(chunk[:4], "big")
        v1 = int.from_bytes(chunk[4:], "big")
        blocks.append((v0, v1))
    return blocks

def blocks_to_bytes(blocks):
    result = b''
    for v0, v1 in blocks:
        result += v0.to_bytes(4, 'big') + v1.to_bytes(4, 'big')
    return result

# ------------------------------------------
# Programa ensamblador
# ------------------------------------------
def generate_crypto_program(start_addr, output_addr, n_blocks, mode):
    op = "ENC32" if mode == "encrypt" else "DEC32"
    loop_label = "loop_enc" if mode == "encrypt" else "loop_dec"

    return [
        "LOADK K0, 0xDEADBEEF, 0xDEADBEEF, 0xDEADBEEF, 0xDEADBEEF",
        f"MOV R3, #{start_addr}",              # i = start
        f"MOV R4, #{start_addr + n_blocks*2}", # final = start + (bloques * 2)
        f"{loop_label}:",
        "MOV R1, R3",                           # dirección de entrada
        "MOVB R1",
        f"{op} K0",
        f"ADD #{output_addr}, R3, R2",         # dirección de salida
        "STB R2",
        "ADD R3, #2, R3",                      # i += 2
        f"BNE R3, R4, {loop_label}",
        "HALT"
    ]

# ------------------------------------------
# Encriptar archivo
# ------------------------------------------
def encrypt_file(input_filename, encrypted_filename):
    blocks = read_file_to_blocks(input_filename)
    if len(blocks) * 2 + 1000 >= len(cpu.data_memory):
        raise MemoryError(f"El archivo es demasiado grande. data_memory insuficiente para {len(blocks)} bloques.")
    cpu.reset()

    # Guardar bloques en memoria
    for i, (v0, v1) in enumerate(blocks):
        cpu.data_memory[i * 2] = v0
        cpu.data_memory[i * 2 + 1] = v1

    program = generate_crypto_program(start_addr=0, output_addr=1000, n_blocks=len(blocks), mode="encrypt")
    assembled = assemble(program)
    cpu.load_program(assembled)
    cpu.run()

    # Extraer datos cifrados
    enc_blocks = []
    for i in range(len(blocks)):
        v0 = cpu.data_memory[1000 + i * 2]
        v1 = cpu.data_memory[1000 + i * 2 + 1]
        enc_blocks.append((v0, v1))

    with open(encrypted_filename, "wb") as f:
        f.write(blocks_to_bytes(enc_blocks))

    # Calcular hash
    with open(encrypted_filename, "rb") as f:
        file_hash = md5(f.read()).hexdigest()

    print(f"[✓] Archivo encriptado: {encrypted_filename}")
    print(f"[✓] Hash MD5: {file_hash}")

# ------------------------------------------
# Desencriptar archivo .enc
# ------------------------------------------
def decrypt_file(encrypted_filename, output_filename):
    blocks = read_file_to_blocks(encrypted_filename)
    if len(blocks) * 2 + 1000 >= len(cpu.data_memory):
        raise MemoryError(f"El archivo es demasiado grande. data_memory insuficiente para {len(blocks)} bloques.")

    cpu.reset()

    # Guardar bloques en memoria
    for i, (v0, v1) in enumerate(blocks):
        cpu.data_memory[i * 2] = v0
        cpu.data_memory[i * 2 + 1] = v1

    program = generate_crypto_program(start_addr=0, output_addr=1000, n_blocks=len(blocks), mode="decrypt")
    assembled = assemble(program)
    cpu.load_program(assembled)
    cpu.run()

    # Extraer datos desencriptados
    dec_blocks = []
    for i in range(len(blocks)):
        v0 = cpu.data_memory[1000 + i * 2]
        v1 = cpu.data_memory[1000 + i * 2 + 1]
        dec_blocks.append((v0, v1))

    with open(output_filename, "wb") as f:
        f.write(blocks_to_bytes(dec_blocks))

    print(f"Archivo desencriptado: {output_filename}")

if __name__ == "__main__":
    encrypt_file("jorge_luis.txt", "jorge_luis.txt.enc")
    time.sleep(10)
    decrypt_file("jorge_luis.txt.enc", "jorge_luis_decrypted.txt")
