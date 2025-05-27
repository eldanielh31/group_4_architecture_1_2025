from instrucciones.branch import BranchEqual
from instrucciones.loadWord import LoadWord
from instrucciones.storeWord import StoreWord
from instrucciones.add import Add
from instrucciones.addi import Addi
from instrucciones.sub import Sub
from instrucciones.subi import Subi
from instrucciones.and_ import And
from instrucciones.or_ import Or
from instrucciones.mov import Mov

from procesador.procesador import Procesador
from instrucciones.assembler import assemble

import sys

if __name__ == "__main__":
    # Leer intervalo desde argumentos de la línea de comandos (si no, usar 1 por defecto)
    interval = float(sys.argv[1]) if len(sys.argv) > 1 else 1.0

    # Crear el procesador con el intervalo especificado
    procesador = Procesador(interval=interval)

    # Configurar registros iniciales
    procesador.RF.registros[0] = 0
    procesador.RF.registros[1] = 7
    procesador.RF.registros[2] = 7
    procesador.RF.registros[9] = 5
    procesador.RF.registros[10] = 10
    

    # Cargar instrucciones
    """
    procesador.cargarInstrucciones(StoreWord(0, -4, 4, procesador))
    procesador.cargarInstrucciones(StoreWord(1, -3, 4, procesador))
    procesador.cargarInstrucciones(BranchEqual(0, 1, 4, procesador))
    procesador.cargarInstrucciones(Add(2, 0, 1, procesador))
    procesador.cargarInstrucciones(Addi(3, 0, 3, procesador))
    procesador.cargarInstrucciones(Sub(4, 0, 1, procesador))
    procesador.cargarInstrucciones(Subi(5, 0, 3, procesador))
    procesador.cargarInstrucciones(And(6, 9, 10, procesador))
    procesador.cargarInstrucciones(Or(7, 9, 10, procesador))
    procesador.cargarInstrucciones(Mov(8, 54, procesador))
    """

    with open("program.asm") as f:
        source = f.readlines()
        program = assemble(source)
        print(program)
        procesador.cargarInstrucciones(program)
    

    # Iniciar ejecución del procesador
    procesador.iniciarEjecucion()

