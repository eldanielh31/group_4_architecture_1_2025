; Programa de cifrado y descifrado TEA en pipeline
; Cargar clave K0 en la bóveda
LOADK K0, 0xA1B2C3D4, 0x11223344, 0x55667788, 0x99AABBCC

; Cargar bloque desde memoria[0] y memoria[1] en R1 y R2
MOVB 0

; Cifrar R1 y R2 con clave K0, guardar en R3 y R4
ENC32 0

; Guardar resultado cifrado en memoria[10] y memoria[11]
STB 10

; Cargar desde memoria[10] y [11] en R1 y R2
MOVB 10

; Descifrar bloque con K0, resultado en R3 y R4
DEC32 0

; Guardar resultado descifrado en memoria[20] y memoria[21]
STB 20

; Finalizar ejecución
HALT
