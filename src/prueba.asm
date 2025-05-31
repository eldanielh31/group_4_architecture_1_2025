LOADK 0, 0xA56BABCD, 0x0000FACE, 0xDEADBEEF, 0x12345678  ; Clave de 128 bits en vault[0]

; Cifrar bloque 0 (Mem[0] y Mem[1])
MOVB #0
ENC32 0
STB #20

; Cifrar bloque 1 (Mem[2] y Mem[3])
MOVB #2
ENC32 0
STB #22

HALT
