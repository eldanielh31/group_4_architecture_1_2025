class ENC32:
    def __init__(self, kid, procesador):
        self.kid = kid
        self.procesador = procesador
        self.rounds = 0
        self.sum_ = 0
        self.delta = 0x9e3779b9
        self.v0 = procesador.regCrypt.get('v0', 0)
        self.v1 = procesador.regCrypt.get('v1', 0)
        self.key = procesador.vault[kid]
        self.phase = 0
        self.mode = "ENC"

    def instruccion1(self):  # Execute
        if self.rounds < 32:
            self.sum_ = (self.sum_ + self.delta) & 0xFFFFFFFF
            self.v0 = (self.v0 + (((self.v1 << 4) + self.key[0]) ^ (self.v1 + self.sum_) ^ ((self.v1 >> 5) + self.key[1]))) & 0xFFFFFFFF
            self.v1 = (self.v1 + (((self.v0 << 4) + self.key[2]) ^ (self.v0 + self.sum_) ^ ((self.v0 >> 5) + self.key[3]))) & 0xFFFFFFFF
            self.rounds += 1
            print(f"ENC32 ronda {self.rounds}: v0={hex(self.v0)} v1={hex(self.v1)}")
        else:
            self.phase += 1  # Pasar a siguiente fase

    def instruccion2(self):  # Memory (dummy o guardado temporal)
        print("ENC32 Memory: Preparando para writeback")

    def instruccion3(self):  # Writeback
        self.procesador.regCrypt['v0'] = self.v0
        self.procesador.regCrypt['v1'] = self.v1
        print(f"ENC32 Writeback: Guardando resultado en regCrypt v0={hex(self.v0)} v1={hex(self.v1)}")

    def ejecutar(self):
        if self.phase == 0:
            self.instruccion1()
            # Si rondas completas, avanzar fase
            if self.rounds >= 32:
                self.phase = 1
        elif self.phase == 1:
            self.instruccion2()
            self.phase = 2
        elif self.phase == 2:
            self.instruccion3()
            self.phase = 3
        else:
            print("ENC32 finalizado")