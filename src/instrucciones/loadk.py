class LOADK:
    def __init__(self, kid, key_parts, procesador):
        self.kid = kid
        self.key_parts = key_parts
        self.procesador = procesador
        self.phase = 0  # Controla la fase dentro del pipeline
        print(f"LOADK inicializado con kid={self.kid} y key_parts={self.key_parts}")

    def instruccion1(self):  # Execute
        print(f"LOADK Execute: Cargando clave para kid={self.kid}")
        # Carga la clave temporalmente en registro dedicado
        self.procesador.regCrypt['key'] = self.key_parts

    def instruccion2(self):  # Memory (opcional)
        print(f"LOADK Memory: Preparando actualización de vault")

    def instruccion3(self):  # Writeback
        print(f"LOADK Writeback: Actualizando vault[{self.kid}]")
        self.procesador.vault[self.kid] = self.procesador.regCrypt['key']
        # Limpieza opcional
        self.procesador.regCrypt['key'] = None

    def ejecutar(self):
        if self.phase == 0:
            self.instruccion1()
            self.phase += 1
        elif self.phase == 1:
            self.instruccion2()
            self.phase += 1
        elif self.phase == 2:
            self.instruccion3()
            self.phase += 1
        else:
            print("LOADK finalizado")