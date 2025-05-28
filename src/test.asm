MOV R1, #5
MOV R2, #5
BEQ R1, R2, igual
MOV R3, #99
JMP fin
igual:  
MOV R3, #42
fin:    
HALT
