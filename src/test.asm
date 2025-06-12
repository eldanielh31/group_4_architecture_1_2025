; ---------- Inicializar clave ----------
LOADK K0, 0x01234567, 0x89ABCDEF, 0xFEDCBA98, 0x76543210

; ---------- Prueba de MOV (registros) ----------
MOV R1, #5           ; R1 = 5
MOV R2, R1           ; R2 = 5
MOV R3, #10          ; R3 = 10

; ---------- Prueba de ST y LD ----------
ST R2, R3            ; Mem[10] = R2 (5)
LD R4, R3            ; R4 = Mem[10] = 5

; ---------- Prueba de operaciones aritméticas ----------
ADD R1, R3, R5       ; R5 = R1 + R3 = 5 + 10 = 15
SUB R3, R1, R6       ; R6 = 10 - 5 = 5
XOR R1, R3, R7       ; R7 = 5 XOR 10
SHL R1, #1, R8       ; R8 = 5 << 1 = 10
SHR R3, #1, R9       ; R9 = 10 >> 1 = 5

; ---------- Guardar resultados en memoria ----------
ST R4, #20           ; Mem[20] = R4 (5, desde LD)
ST R5, #22           ; Mem[22] = R5 (15, ADD)
ST R6, #24           ; Mem[24] = R6 (5, SUB)
ST R7, #26           ; Mem[26] = R7 (XOR)
ST R8, #28           ; Mem[28] = R8 (SHL)
ST R9, #30           ; Mem[30] = R9 (SHR)

; ---------- Probar MOVB y STB ----------
MOV R10, #0
MOVB R10             ; carga desde Mem[0] y [1] a V0, V1
ENC32 K0
MOV R11, #40
STB R11              ; guardar C0, C1 en Mem[40], [41]

MOVB R11             ; cargar C0, C1 como entrada
DEC32 K0
MOV R12, #50
STB R12              ; resultado descifrado a Mem[50], [51]

; ---------- Prueba de saltos ----------
MOV R13, #1
MOV R14, #2
BEQ R13, R14, salto_fallido
MOV R15, #6 ; se ejecuta

salto_fallido:
BNE R13, R14, salto_exitoso
MOV R0, #5 ; no se ejecuta

salto_exitoso:
JMP fin_salto
MOV R0, #5 ; no se ejecuta

fin_salto:
MOV R0, #5 ; se ejecuta

; ---------- NOP ----------
NOP
NOP

; ---------- Final ----------
HALT
