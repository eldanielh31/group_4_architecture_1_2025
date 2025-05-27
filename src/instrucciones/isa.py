from instrucciones.add import ADD
from instrucciones.sub import SUB
from instrucciones.xor import XOR
from instrucciones.loadWord import LD
from instrucciones.storeWord import ST
from instrucciones.mov import MOV
from instrucciones.movb import MOVB
ISA = {
    "LOADK": 0x01,  # Cargar clave en bóveda
    "ENC32": 0x02,  # Cifrado TEA
    "DEC32": 0x03,  # Descifrado TEA (Gambo)
    "MOVB":  MOVB,  # Cargar bloque desde memoria a R1/R2 (Gambo)
    "STB":   0x05,  # Guardar resultado en memoria desde R3/R4
    "MOV":   MOV,  # Movimiento general (no usado actualmente)
    "LD":    LD,  # Cargar desde memoria (por dirección) a un registro
    "ST":    ST,  # Guardar desde un registro a memoria
    "ADD":   ADD,  # Suma
    "SUB":   SUB,  # Resta
    "XOR":   XOR,  # XOR lógico
    "SHL":   0x0C,  # Shift izquierda
    "SHR":   0x0D,  # Shift derecha
    "JMP":   0x0E,  # Salto incondicional
    "BEQ":   0x0F,  # Salto si iguales
    "BNE":   0x10,  # Salto si diferentes
    "HALT":  "HALT"
}
