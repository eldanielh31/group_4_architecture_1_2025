# descifrar.py

from assembler import assemble
from cpu import load_program, run, data_memory
from pathlib import Path
import hashlib

INPUT_FILE = "jorge_luis.txt.enc"
OUTPUT_FILE = "jorge_luis_decrypted.txt"
KEY_HEX = [
    0xDEADBEEF,
    0xDEADBEEF,
    0xDEADBEEF,
    0xDEADBEEF
]

def load_encrypted_file_to_memory(filepath):
    content = Path(filepath).read_bytes()
    # Asume que fue cifrado en bloques de 8 bytes = 2 palabras de 4 bytes
    for i in range(0, len(content), 4):
        word = int.from_bytes(content[i:i+4], byteorder="big")
        data_memory[i // 4] = word

def write_output_from_memory(filepath, start_addr, byte_count):
    with open(filepath, "wb") as f:
        for i in range(start_addr, start_addr + byte_count, 4):
            word = data_memory[i // 4]
            f.write(word.to_bytes(4, byteorder="big"))

def main():
    # Instrucciones para descifrar (como las que usaste tú)
    asm_code = f"""
    LOADK K0, 0x{KEY_HEX[0]:08X}, 0x{KEY_HEX[1]:08X}, 0x{KEY_HEX[2]:08X}, 0x{KEY_HEX[3]:08X}

    MOV R3, #0       ; i = 0
    MOV R4, #{len(Path(INPUT_FILE).read_bytes())} ; fin

    loop:
    MOV R1, R3
    MOVB R1
    DEC32 K0
    ADD R3, #10, R2
    STB R2
    ADD R3, #2, R3
    BNE R3, R4, loop

    HALT
    """.strip().splitlines()

    # Cargar archivo cifrado en memoria
    load_encrypted_file_to_memory(INPUT_FILE)

    # Ensamblar y ejecutar
    program = assemble(asm_code)
    load_program(program)
    run()

    # Guardar el archivo descifrado
    write_output_from_memory(OUTPUT_FILE, 10, len(Path(INPUT_FILE).read_bytes()))

    # Mostrar hash
    md5 = hashlib.md5(Path(OUTPUT_FILE).read_bytes()).hexdigest()
    print(f"✅ Archivo descifrado guardado como: {OUTPUT_FILE}")
    print(f"🔐 MD5 del archivo descifrado: {md5}")

if __name__ == "__main__":
    main()
