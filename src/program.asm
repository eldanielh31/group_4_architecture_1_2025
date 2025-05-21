; Cargar clave en la bóveda K0
LOADK K0, 0xA1B2C3D4, 0x11223344, 0x55667788, 0x99AABBCC

; Cargar bloque (v0, v1) desde memoria[0] y memoria[1] a registros R1 y R2
MOVB 0

; Cifrar R1 y R2 usando la clave K0 → resultado en R3 y R4
ENC32 0

; Guardar resultado cifrado (R3, R4) en memoria[10] y memoria[11]
STB 10

; Cargar el bloque cifrado (memoria[10..11]) en R1 y R2 para descifrarlo
MOVB 10

; Descifrar el bloque con la misma clave K0 → resultado en R3 y R4
DEC32 0

; Guardar resultado descifrado en memoria[20] y memoria[21]
STB 20

; Finalizar ejecución
HALT
