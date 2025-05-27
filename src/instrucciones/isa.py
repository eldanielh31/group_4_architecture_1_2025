ISA = {
    "LOADK": 0x01,  # Cargar clave en bóveda
    "ENC32": 0x02,  # Cifrado TEA
    "DEC32": 0x03,  # Descifrado TEA
    "MOVB":  0x04,  # Cargar bloque desde memoria a R1/R2
    "STB":   0x05,  # Guardar resultado en memoria desde R3/R4
    "MOV":   0x06,  # Movimiento general (no usado actualmente)
    "LD":    0x07,  # Cargar desde memoria (por dirección) a un registro
    "ST":    0x08,  # Guardar desde un registro a memoria
    "ADD":   0x09,  # Suma
    "SUB":   0x0A,  # Resta
    "XOR":   0x0B,  # XOR lógico
    "SHL":   0x0C,  # Shift izquierda
    "SHR":   0x0D,  # Shift derecha
    "JMP":   0x0E,  # Salto incondicional
    "BEQ":   0x0F,  # Salto si iguales
    "BNE":   0x10,  # Salto si diferentes
    "HALT":  0xFF
}
