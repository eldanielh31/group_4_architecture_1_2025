
from isa import ISA

def assemble(lines):
    program = []
    for line in lines:
        line = line.strip()
        if not line or line.startswith(";"):
            continue
        parts = line.replace(",", "").split()
        instr = parts[0].upper()
        if instr == "LOADK":
            program.append([ISA[instr], int(parts[1][1]), int(parts[2], 16), int(parts[3], 16), int(parts[4], 16), int(parts[5], 16)])
        elif instr in ["MOVB", "ENC32", "DEC32", "STB"]:
            program.append([ISA[instr], int(parts[1])])
        elif instr == "HALT":
            program.append([ISA[instr]])
    return program
