class StoreWord:
    def __init__(self, _fuente, _inmediato, _destino, _procesador):
        self.destino = _destino
        self.inmediato = _inmediato
        self.fuente = _fuente
        self.procesador = _procesador

        self.ejecucion = [self.instruccion1, self.instruccion2, self.instruccion3]

    def instruccion1(self):
        print("Obteniendo de registro "+str(self.fuente))
        self.procesador.regRF.data = self.procesador.RF.registros[self.fuente]
        print(self.procesador.regRF.data)

    def instruccion2(self):
        print("Obteniendo nueva direccion de memoria")
        self.procesador.regALU.data = [None] * 2
        self.procesador.regALU.data[0] = self.procesador.ALU.operar(self.destino, self.inmediato, 0)
        self.procesador.regALU.data[1] = self.procesador.regRF.data
        print(self.procesador.regALU.data)

    def instruccion3(self):
        print("Almacenando en direccion de memoria " + str(self.procesador.regALU.data[0]))
        self.procesador.DM.datos[self.procesador.regALU.data[0]] = self.procesador.regALU.data[1]
        print(self.procesador.regALU.data[1])



    def ejecutar(self):
        if self.ejecucion:
            fase = self.ejecucion.pop(0)
            fase()
        else:
            print("No hay más fases para ejecutar en StoreWord.")







