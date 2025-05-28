
from isa import ISA

def parse_register(s):
    if s.startswith('R'):
        reg = int(s[1:])
        if not (0 <= reg < 16):
            raise ValueError(f"Invalid register R{reg}")
        return reg
    elif s.startswith('#'):
        return int(s[1:])
    elif s.startswith('K'):
        return int(s[1:])
    else:
        return int(s)

def assemble(lines):
    program = []
    label_table = {}
    output = []

    # Primera pasada: capturar etiquetas
    pc = 0
    for lineno, line in enumerate(lines, 1):
        line = line.strip()
        if not line or line.startswith(";"):
            continue
        if ":" in line:
            label = line.split(":")[0].strip()
            label_table[label] = pc
            line = line.split(":", 1)[1].strip()
            if not line:
                continue
        if line:
            pc += 1

    # Segunda pasada: convertir a instrucciones
    for lineno, line in enumerate(lines, 1):
        line = line.strip()
        if not line or line.startswith(";"):
            continue
        if ":" in line:
            line = line.split(":", 1)[1].strip()
            if not line:
                continue
        try:
            parts = line.replace(",", "").split()
            instr = parts[0].upper()

            if instr not in ISA:
                raise ValueError(f"Unknown instruction '{instr}'")

            if instr == "LOADK":
                output.append([ISA[instr], parse_register(parts[1]),
                               int(parts[2], 16), int(parts[3], 16),
                               int(parts[4], 16), int(parts[5], 16)])
            elif instr in ["MOVB", "ENC32", "DEC32", "STB"]:
                output.append([ISA[instr], parse_register(parts[1])])
            elif instr in ["ADD", "SUB", "XOR", "SHL", "SHR"]:
                output.append([ISA[instr], parse_register(parts[1]), parse_register(parts[2]), parse_register(parts[3])])
            elif instr in ["LD", "ST"]:
                output.append([ISA[instr], parse_register(parts[1]), parse_register(parts[2])])
            elif instr == "MOV":
                dest = parse_register(parts[1])
                if parts[2].startswith('#'):
                    value = int(parts[2][1:])
                    output.append([ISA[instr], dest, ('#', value)])
                else:
                    value = parse_register(parts[2])
                    output.append([ISA[instr], dest, value])
            elif instr == "JMP":
                target = label_table[parts[1]]
                output.append([ISA[instr], target])
            elif instr in ["BEQ", "BNE"]:
                reg1 = parse_register(parts[1])
                reg2 = parse_register(parts[2])
                label = parts[3]
                if label not in label_table:
                    raise ValueError(f"Undefined label '{label}'")
                output.append([ISA[instr], reg1, reg2, label_table[label]])
            elif instr == "HALT":
                output.append([ISA[instr]])
            elif instr == "NOP":
                output.append([ISA["NOP"]])
            else:
                raise ValueError(f"Unhandled instruction '{instr}'")

        except Exception as e:
            raise SyntaxError(f"Error on line {lineno}: {line}\n{e}")

    return output