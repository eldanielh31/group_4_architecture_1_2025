from instrucciones.add import ADD
from instrucciones.sub import SUB
from instrucciones.xor import XOR
from instrucciones.loadWord import LD
from instrucciones.storeWord import ST
from instrucciones.mov import MOV
from instrucciones.movb import MOVB
from instrucciones.loadk import LOADK
ISA = {
    "LOADK": LOADK,  # Cargar clave en bóveda

    "MOVB":  MOVB,  # Cargar bloque desde memoria a R1/R2 (Gambo)

    "MOV":   MOV,  # Movimiento general (no usado actualmente)
    "LD":    LD,  # Cargar desde memoria (por dirección) a un registro
    "ST":    ST,  # Guardar desde un registro a memoria
    "ADD":   ADD,  # Suma
    "SUB":   SUB,  # Resta
    "XOR":   XOR,  # XOR lógico

    "HALT":  "HALT"
}
