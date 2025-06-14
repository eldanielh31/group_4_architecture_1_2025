; ---------- Inicializar clave ----------
LOADK K0, 0x01234567, 0x89ABCDEF, 0xFEDCBA98, 0x76543210

;---------- Prueba de Intrucción -----------
MOVB R0
ENC32 K0
; ---------- Final ----------
HALT
