class LoadWord:
    def __init__(self, _destino, _inmediato, _fuente, _procesador):
        self.destino = _destino
        self.inmediato = _inmediato
        self.fuente = _fuente
        self.procesador = _procesador

        self.ejecucion = [self.instruccion1, self.instruccion2, self.instruccion3, self.instruccion4]

    def instruccion1(self):
        print("Obteniendo de registro " + str(self.fuente))
        self.procesador.regRF.data = self.procesador.RF.registros[self.fuente]
        print(self.procesador.regRF.data)

    def instruccion2(self):
        print("Obteniendo nueva direccion de memoria")
        self.procesador.regALU.data = self.procesador.ALU.operar(self.procesador.regRF.data, self.inmediato, 0)
        print(self.procesador.regALU.data)

    def instruccion3(self):
        print("Obteniendo dato de memoria")
        self.procesador.regDM.data = self.procesador.DM.datos[self.procesador.regALU.data]
        print(self.procesador.regDM.data)

    def instruccion4(self):
        print("Escribiendo en el registro " + str(self.destino))
        self.procesador.RF.registros[self.destino] = self.procesador.regDM.data
        print(self.procesador.RF.registros[self.destino])

    def ejecutar(self):
        if self.ejecucion:
            fase = self.ejecucion.pop(0)
            fase()
        else:
            print("No hay más fases para ejecutar en LoadWord.")
