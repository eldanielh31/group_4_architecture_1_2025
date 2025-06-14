; ---------- Inicializar clave ----------
LOADK K0, 0x01234567, 0x89ABCDEF, 0xFEDCBA98, 0x76543210

;---------- Prueba de Instrucción -----------
MOVB R0
ENC32 K0
STB R11
MOV R2, R1           ; R2 = 5
ST R2, R3            ; Mem[10] = R2 (5)
LD R4, R3            ; R4 = Mem[10] = 5
DEC32 K0
; ---------- Prueba de operaciones aritméticas ----------
ADD R1, R3, R5       ; R5 = R1 + R3 = 5 + 10 = 15
SUB R3, R1, R6       ; R6 = 10 - 5 = 5
XOR R1, R3, R7       ; R7 = 5 XOR 10
SHL R1, R6, R8       ; R8 = 5 << 1 = 10
SHR R3, R7, R9       ; R9 = 10 >> 1 = 5

; ---------- Guardar resultados en memoria ----------
ST R4, 20           ; Mem[20] = R4 (5, desde LD)
ST R5, 22           ; Mem[22] = R5 (15, ADD)
ST R6, 24           ; Mem[24] = R6 (5, SUB)
ST R7, 26           ; Mem[26] = R7 (XOR)
ST R8, 28           ; Mem[28] = R8 (SHL)
ST R9, 30           ; Mem[30] = R9 (SHR)

; ---------- Final ----------
HALT
