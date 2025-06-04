LOADK K0, 0xA56BABCD, 0x0000FFFF, 0x12345678, 0x87654321

MOV R3, #0      ; i = 0
MOV R4, #6      ; número de bloques = 3 bloques * 2 (porque cada bloque tiene 2 palabras)

; Bucle de cifrado
cifrar_loop:
MOV R1, R3      ; dirección de entrada
MOVB R1
ENC32 K0
ADD #10, R3, R2 ; dirección de salida cifrada
STB R2
ADD R3, #2, R3 ; i += 2
BNE R3, R4, cifrar_loop

MOV R3, #10     ; i = 10
MOV R4, #16     ; fin = 10 + (3 bloques * 2)

; Bucle de descifrado
descifrar_loop:
MOV R1, R3
MOVB R1
DEC32 K0
ADD #10, R3, R2 ; dirección de salida descifrada
STB R2
ADD R3, #2, R3 ; i += 2
BNE R3, R4, descifrar_loop

HALT
