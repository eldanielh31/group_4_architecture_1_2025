import time
import cpu
from assembler import assemble
from hashlib import md5
import os

BLOCK_BATCH = 400

# ------------------------------------------
# Utilidades para conversión
# ------------------------------------------
def read_file_to_blocks(filename):
    with open(filename, "rb") as f:
        data = f.read()
    blocks = []
    for i in range(0, len(data), 8):
        chunk = data[i:i+8].ljust(8, b"\x00")
        v0 = int.from_bytes(chunk[:4], "little")
        v1 = int.from_bytes(chunk[4:], "little")
        blocks.append((v0, v1))
    return blocks

def blocks_to_bytes(blocks):
    result = b''
    for v0, v1 in blocks:
        result += v0.to_bytes(4, 'little') + v1.to_bytes(4, 'little')
    return result

# ------------------------------------------
# Utilidad para cargar y preparar programa ASM
# ------------------------------------------
def load_asm_with_blocks(template_path, n_blocks):
    with open(template_path, "r") as f:
        lines = f.read()
    program_text = lines.replace("{{N_BLOCKS}}", str(n_blocks))
    return [line.strip() for line in program_text.splitlines() if line.strip()]

# ------------------------------------------
# Encriptar archivo
# ------------------------------------------
def encrypt_file(input_filename, encrypted_filename, log_filename):
    blocks = read_file_to_blocks(input_filename)
    original_file_size = os.path.getsize(input_filename)

    encrypted_blocks = []
    with open(log_filename, "w") as log:
        log.write(f"[Debug] Encriptando bloques (archivo original: {original_file_size} bytes):\n")

    for batch_start in range(0, len(blocks), BLOCK_BATCH):
        batch = blocks[batch_start:batch_start + BLOCK_BATCH]
        cpu.reset()
        for i, (v0, v1) in enumerate(batch):
            cpu.data_memory[i * 2] = v0
            cpu.data_memory[i * 2 + 1] = v1

        program = load_asm_with_blocks("encrypt_loop.asm", len(batch))
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

        program = load_asm_with_blocks("decrypt_loop.asm", len(batch))
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

    raw_bytes = blocks_to_bytes(decrypted_blocks).rstrip(b"\x00")

    with open(output_filename, "wb") as f:
        f.write(raw_bytes)

    print(f"[✓] Archivo desencriptado: {output_filename}")

def count_blocks(filename):
    """
    Retorna la cantidad de bloques de 8 bytes en el archivo dado.
    """
    file_size = os.path.getsize(filename)
    return (file_size + 7) // 8  # Redondea hacia arriba si hay padding


# ------------------------------------------
# Main
# ------------------------------------------
if __name__ == "__main__":
    encrypt_file("jorge_luis.txt", "jorge_luis.txt.enc", "debug_log.txt")
    time.sleep(5)
    decrypt_file("jorge_luis.txt.enc", "jorge_decrypted.txt", "debug_log.txt")