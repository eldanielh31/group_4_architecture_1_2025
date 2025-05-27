class MOVB:
    def __init__(self, direccion, procesador):
        self.direccion = direccion
        self.procesador = procesador

        # Guarda internamente la dirección base
        self.dir_base = None

        self.ejecucion = [self.instruccion1, self.instruccion2, self.instruccion3, self.instruccion4]

    def instruccion1(self):
        print("Guardando dirección base del bloque desde inmediato")
        self.dir_base = self.direccion
        print("Dirección base:", self.dir_base)

    def instruccion2(self):
        print("Leyendo primer dato del bloque")
        self.procesador.regALU.data = self.procesador.DM.datos[self.dir_base]
        print("Dato 1:", self.procesador.regALU.data)

    def instruccion3(self):
        print("Leyendo segundo dato del bloque")
        self.procesador.regDM.data = self.procesador.DM.datos[self.dir_base + 1]
        print("Dato 2:", self.procesador.regDM.data)

    def instruccion4(self):
        print("Cargando en R1 y R2")
        self.procesador.RF.registros[1] = self.procesador.regALU.data
        self.procesador.RF.registros[2] = self.procesador.regDM.data
        print(f"R1 <- {self.procesador.RF.registros[1]}, R2 <- {self.procesador.RF.registros[2]}")

    def ejecutar(self):
        if self.ejecucion:
            fase = self.ejecucion.pop(0)
            fase()
        else:
            print("MOVB completado.")









