; ---------- Inicializar clave ----------
LOADK K0, 0x01234567, 0x89ABCDEF, 0xFEDCBA98, 0x76543210

;---------- Prueba de Instrucción -----------
MOVB R0
ENC32 K0
STB R11
; ---------- Final ----------
HALT
