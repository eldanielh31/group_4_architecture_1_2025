ISA = {
    "LOADK": 0x01,  # Cargar clave en bóveda
    #TODO: crear
    "ENC32": 0x02,  # Cifrado TEA
    #TODO: crear
    "DEC32": 0x03,  # Descifrado TEA
    #TODO: verificar
    "MOVB":  0x04,  # Cargar bloque desde memoria a R1/R2
    #TODO: verificar
    "STB":   0x05,  # Guardar resultado en memoria desde R3/R4
    "MOV":   0x06,  # Movimiento general (no usado actualmente)
    #TODO: verificar
    "LD":    0x07,  # Cargar desde memoria (por dirección) a un registro
    #TODO: verificar
    "ST":    0x08,  # Guardar desde un registro a memoria
    "ADD":   0x09,  # Suma
    "SUB":   0x0A,  # Resta
    "XOR":   0x0B,  # XOR lógico
    #TODO: verificar
    "SHL":   0x0C,  # Shift izquierda
    #TODO: verificar
    "SHR":   0x0D,  # Shift derecha
    "JMP":   0x0E,  # Salto incondicional
    "BEQ":   0x0F,  # Salto si iguales
    "BNE":   0x10,  # Salto si diferentes
    "NOP":   0x11,
    "HALT":  0xFF
}
