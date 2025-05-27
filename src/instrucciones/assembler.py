from instrucciones.isa import ISA


def assemble(lines, procesador):
    program = []
    for lineno, line in enumerate(lines, 1):
        line = line.strip()
        if not line or line.startswith(";"):
            continue
        try:
            parts = line.replace(",", "").split()
            instr = parts[0].upper()
            if instr not in ISA:
                raise ValueError(f"Unknown instruction '{instr}'")

            if instr == "LOADK":
                if len(parts) != 6:
                    raise ValueError("LOADK expects 5 arguments")
                instance = ISA[instr](int(parts[1][1]),
                                int(parts[2], 16), int(parts[3], 16),
                                int(parts[4], 16), int(parts[5], 16), procesador)
                program.append(instance)

            elif instr in ["MOVB", "ENC32", "DEC32", "STB"]:
                if len(parts) != 2:
                    raise ValueError(f"{instr} expects 1 argument")
                instance = ISA[instr](int(parts[1]), procesador)
                program.append(instance)
               

            elif instr in ["ADD", "SUB", "XOR", "AND", "OR"]:
                if len(parts) != 4:
                    raise ValueError(f"{instr} expects 3 arguments")
                instance = ISA[instr](int(parts[1][1:]), int(parts[2][1:]), int(parts[3][1:]), procesador)
                program.append(instance)

            elif instr in ["SHL", "SHR"]:
                if len(parts) != 3:
                    raise ValueError(f"{instr} expects 2 arguments")
                instance = ISA[instr](int(parts[1][1:]), int(parts[2][1:]), procesador)
                program.append(instance)

            elif instr in ["LD", "ST"]:
                if len(parts) != 4:
                    raise ValueError(f"{instr} expects 2 arguments")
                instance = ISA[instr](int(parts[1][1:]), int(parts[2][1:]), int(parts[3][1:]), procesador)
                program.append(instance)
            elif instr == "HALT":
                program.append(ISA[instr])

            else:
                raise ValueError(f"Unhandled instruction '{instr}'")

        except Exception as e:
            raise SyntaxError(f"Error on line {lineno}: {line}\n{e}")

    return program
