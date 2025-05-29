; Cargar clave K0 en la bóveda
LOADK K0, 0xA1B2C3D4, 0x11223344, 0x55667788, 0x99AABBCC

; Cargar bloque desde memoria[0] y memoria[1] en R1 y R2
MOVB 0

; Cifrar R1 y R2 con clave K0, resultado en R3 y R4
ENC32 K0

STB R10

MOVB R10

; Descifrar bloque con K0, resultado en R3 y R4
DEC32 K0

; Guardar resultado descifrado en memoria[20] y memoria[21]
STB 20

; Segundo bloque: cifrar y descifrar "do"
MOVB 2
ENC32 K0

; Guardar cifrado del segundo bloque en memoria[12] y [13]
STB 12

; Cargar cifrado del segundo bloque
MOVB 12

; Descifrar segundo bloque
DEC32 K0

; Guardar descifrado final en memoria[22] y [23]
STB 22

; Fin
HALT
