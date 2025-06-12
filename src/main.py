from assembler import assemble
import cpu

# ------------------------------------------
# Cargar archivo ensamblador externo
# ------------------------------------------
def load_asm_file(filepath):
    with open(filepath, "r") as f:
        return [line.strip() for line in f if line.strip()]

# ------------------------------------------
# Inicializar memoria si se desea probar instrucciones que usen datos
# ------------------------------------------
def preload_memory():
    # Ejemplo: insertar datos en posiciones fijas
    cpu.data_memory[0] = 0x12345678
    cpu.data_memory[1] = 0x9ABCDEF0
    cpu.data_memory[2] = 0x0F0F0F0F
    cpu.data_memory[3] = 0xF0F0F0F0
    # Puedes añadir más datos si tus instrucciones los requieren
    # Por ejemplo, usar MOV/ST/LD para manipularlos
    print("[✓] Memoria precargada con datos de prueba")

# ------------------------------------------
# Cargar programa desde test.asm
# ------------------------------------------
source = load_asm_file("test.asm")

# Ensamblar y cargar el programa
program = assemble(source)
cpu.load_program(program)

# Precargar datos si necesario
preload_memory()

# Ejecutar el programa
cpu.run()

# ------------------------------------------
# Imprimir estado de memoria para validar
# ------------------------------------------
print("\nEstado final de memoria (primeros 32 registros):")
for i in range(0, 32, 2):
    print(f"Mem[{i:02}] = 0x{cpu.data_memory[i]:08X}, Mem[{i+1:02}] = 0x{cpu.data_memory[i+1]:08X}")
