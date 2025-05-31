LOADK 0, 0xA56BABCD, 0x0000FACE, 0xDEADBEEF, 0x12345678  ; Clave original

; Bloque 1
MOVB #20          ; V0 = Mem[20], V1 = Mem[21]
DEC32 0           ; Descifra usando clave en vault[0]
STB #30           ; Guarda resultado descifrado en Mem[30], Mem[31]

; Bloque 2
MOVB #22          ; V0 = Mem[22], V1 = Mem[23]
DEC32 0
STB #32           ; Resultado en Mem[32], Mem[33]

HALT
