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

# Precarga de datos si aplica

def preload_memory(mod):
    mod.data_memory[1] = 0x9ABCDEF0
    pass

if __name__ == '__main__':
    source = load_asm_file('test.asm')
    program = assemble(source)

    # Configuraciones de CPU
    modules = [
        ('Uniciclo', uniciclo),
        ('Multiciclo', multiciclo),
        ('Pipeline', pipeline),
    ]
    results = []

    for name, mod in modules:
        # Cargar y precargar
        mod.load_program(program)
        preload_memory(mod)

        # Ejecutar
        mod.run()

        # Leer métricas desde el módulo
        cycles = getattr(mod, 'cycle_count', None)
        elapsed = getattr(mod, 'elapsed_time', None)

        results.append((name, cycles, elapsed))
            
        # --- GRÁFICO ---
        nombres = [r[0] for r in results]
        ciclos  = [r[1] if r[1] is not None else 0 for r in results]
        tiempos = [r[2] if r[2] is not None else 0 for r in results]

        x = range(len(nombres))

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(6, 8), sharex=True)

        # Barras para ciclos
        ax1.bar(x, ciclos)
        ax1.set_ylabel('Ciclos')
        ax1.set_title('Comparativa de Ciclos')

        # Barras para tiempo
        ax2.bar(x, tiempos)
        ax2.set_ylabel('Tiempo (s)')
        ax2.set_title('Comparativa de Tiempo de Ejecución')
        ax2.set_xticks(x)
        ax2.set_xticklabels(nombres)

        plt.tight_layout()
        plt.show()
