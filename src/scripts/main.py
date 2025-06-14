from assembler import assemble
import uniciclo as uniciclo
import multiciclo as multiciclo
import pipeline as pipeline
import time
import matplotlib.pyplot as plt

# Cargar ensamblador
def load_asm_file(filepath):
    with open(filepath, 'r') as f:
        return [line.strip() for line in f if line.strip()]

# Precarga de datos
def preload_memory(mod):
    mod.data_memory[0] = 0x9ABCDEF0
    mod.data_memory[1] = 0xAABBCCDD

def preload_registers(mod):
    mod.registers[1] = 0x5
    mod.registers[3] = 0xA

if __name__ == '__main__':
    source = load_asm_file('test.asm')
    program = assemble(source)

    modules = [
        ('Uniciclo', uniciclo),
        ('Multiciclo', multiciclo),
        ('Pipeline', pipeline),
    ]
    results = []

    for name, mod in modules:
        mod.load_program(program)
        preload_memory(mod)
        preload_registers(mod)

        mod.run()

        # Métricas
        elapsed_time = getattr(mod, 'elapsed_time', 1.0)
        instruction_count = getattr(mod, 'instruction_count', 0)

        ips = instruction_count / elapsed_time  # instrucciones por segundo
        mips = ips / 1e6  # millones de instrucciones por segundo

        results.append((name, elapsed_time, ips))

    # Desempaquetar resultados
    names = [r[0] for r in results]
    times = [r[1] for r in results]
    ips_values = [r[2] for r in results]
    x = range(len(names))

    # Crear una figura con 2 subplots verticales
    fig, (ax_time, ax_throughput) = plt.subplots(2, 1, figsize=(8, 8), sharex=True)

    # 1) Tiempo de ejecución
    ax_time.bar(x, times, color='salmon')
    ax_time.set_ylabel('Tiempo (s)')
    ax_time.set_title('Comparativa de Tiempo de Ejecución')

    # 2) Throughput (MIPS)
    ax_throughput.bar(x, ips_values, color='mediumseagreen')
    ax_throughput.set_ylabel('IPS')
    ax_throughput.set_title('Throughput (Instrucciones por Segundo)')
    ax_throughput.set_xticks(x)
    ax_throughput.set_xticklabels(names)

    plt.tight_layout()
    plt.show()

