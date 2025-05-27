class Subi:
    def __init__(self, _destino, _registro1, _inmediate, _procesador):
        self.destino = _destino
        self.registro1 = _registro1
        self.inmediate = _inmediate
        self.procesador = _procesador

        self.ejecucion = [self.instruccion1, self.instruccion2, self.instruccion3]

    def instruccion1(self):
        print("Obteniendo de registro "+str(self.registro1))
        
        self.procesador.regRF.data = self.procesador.RF.registros[self.registro1]
        
        print(self.procesador.regRF.data)

    def instruccion2(self):
        print("Restando ")
        self.procesador.regALU.data = self.procesador.ALU.operar(self.procesador.regRF.data, self.inmediate, 1)
        print(self.procesador.regALU.data)

    def instruccion3(self):
        print("Guardando resultado en registros")
        self.procesador.RF.registros[self.destino] = self.procesador.regALU.data
        print(str(self.procesador.RF.registros[self.destino]) + " en: " + str(self.destino))


        

    def ejecutar(self):
        if self.ejecucion:
            fase = self.ejecucion.pop(0)
            fase()
        else:
            print("No hay más fases para ejecutar en SubI.")







