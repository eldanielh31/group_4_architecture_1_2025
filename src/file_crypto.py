import time
import cpu
from assembler import assemble
from hashlib import md5
import os

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
    program = ["LOADK K0, 0xDEADBEEF, 0xDEADBEEF, 0xDEADBEEF, 0xDEADBEEF"]

    for i in range(n_blocks):
        input_addr = start_addr + i * 2
        output_addr_i = output_addr + i * 2
        program.extend([
            f"MOV R3, #{input_addr}",
            "MOV R1, R3",
            "MOVB R1",
            "NOP",
            f"{op} K0",
            "NOP",
            f"MOV R2, #{output_addr_i}",
            "NOP",
            "STB R2",
            "NOP",
        ])
    program.append("HALT")
    return program

# ------------------------------------------
# Control de tamaño de memoria
# ------------------------------------------
def check_blocks(blocks):
    if len(blocks) * 2 + 1000 >= len(cpu.data_memory):
        raise MemoryError("Archivo muy grande. Memoria insuficiente.")

# ------------------------------------------
# Encriptar archivo
# ------------------------------------------
BLOCK_BATCH = 400

def encrypt_file(input_filename, encrypted_filename, log_filename):
    blocks = read_file_to_blocks(input_filename)
    original_file_size = os.path.getsize(input_filename)

    # Guardar copia original y tamaño
    with open("original_blocks.bin", "wb") as f:
        f.write(blocks_to_bytes(blocks))
    with open("original_size.txt", "w") as f:
        f.write(str(original_file_size))

    encrypted_blocks = []
    with open(log_filename, "w") as log:
        log.write(f"[Debug] Encriptando bloques (archivo original: {original_file_size} bytes):\n")

    for batch_start in range(0, len(blocks), BLOCK_BATCH):
        batch = blocks[batch_start:batch_start + BLOCK_BATCH]
        cpu.reset()
        for i, (v0, v1) in enumerate(batch):
            cpu.data_memory[i * 2] = v0
            cpu.data_memory[i * 2 + 1] = v1

        program = generate_crypto_program(start_addr=0, output_addr=1000, n_blocks=len(batch), mode="encrypt")
        assembled = assemble(program)
        cpu.load_program(assembled)
        cpu.run()

        with open(log_filename, "a") as log:
            for i in range(len(batch)):
                v0 = cpu.data_memory[i * 2]
                v1 = cpu.data_memory[i * 2 + 1]
                c0 = cpu.data_memory[1000 + i * 2]
                c1 = cpu.data_memory[1000 + i * 2 + 1]
                log.write(f"[Block {batch_start + i}] IN: V0=0x{v0:08X}, V1=0x{v1:08X} -> C0=0x{c0:08X}, C1=0x{c1:08X}\n")
                encrypted_blocks.append((c0, c1))

    with open(encrypted_filename, "wb") as f:
        f.write(blocks_to_bytes(encrypted_blocks))

    with open(encrypted_filename, "rb") as f:
        file_hash = md5(f.read()).hexdigest()

    print(f"[✓] Archivo encriptado: {encrypted_filename}")
    print(f"[✓] Hash MD5: {file_hash}")

# ------------------------------------------
# Desencriptar archivo
# ------------------------------------------
def decrypt_file(encrypted_filename, output_filename, log_filename):
    blocks = read_file_to_blocks(encrypted_filename)
    decrypted_blocks = []

    with open(log_filename, "a") as log:
        log.write("\n[Debug] Desencriptando bloques (sin verificación de original):\n")

    for batch_start in range(0, len(blocks), BLOCK_BATCH):
        batch = blocks[batch_start:batch_start + BLOCK_BATCH]
        cpu.reset()
        for i, (v0, v1) in enumerate(batch):
            cpu.data_memory[i * 2] = v0
            cpu.data_memory[i * 2 + 1] = v1

        program = generate_crypto_program(start_addr=0, output_addr=1000, n_blocks=len(batch), mode="decrypt")
        assembled = assemble(program)
        cpu.load_program(assembled)
        cpu.run()

        with open(log_filename, "a") as log:
            for i in range(len(batch)):
                d0 = cpu.data_memory[1000 + i * 2]
                d1 = cpu.data_memory[1000 + i * 2 + 1]
                index = batch_start + i
                log.write(f"[Block {index}] OUT: V0=0x{d0:08X}, V1=0x{d1:08X}\n")
                decrypted_blocks.append((d0, d1))

    # Convertir a bytes y quitar padding final
    raw_bytes = blocks_to_bytes(decrypted_blocks).rstrip(b"\x00")

    with open(output_filename, "wb") as f:
        f.write(raw_bytes)

    print(f"[✓] Archivo desencriptado: {output_filename}")


# ------------------------------------------
# Main
# ------------------------------------------
if __name__ == "__main__":
    #encrypt_file("imagen.png", "imagen.png.enc", "debug_log.txt")
    #time.sleep(3)
    #decrypt_file("encrypted_image.png", "imagen_restaurada.png", "debug_log.txt")

    encrypt_file("jorge_luis.txt", "jorge_luis.txt.enc", "debug_log.txt")
    #time.sleep(3)
    #decrypt_file("jorge_luis.txt.enc", "jorge.txt", "debug_log.txt")
