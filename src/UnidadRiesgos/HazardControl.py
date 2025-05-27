
from instrucciones.add import Add
from instrucciones.sub import Sub
from instrucciones.and_ import And
from instrucciones.or_ import Or

class HazardControl:
    def __init__(self, procesador):
        self.procesador = procesador

    def handle_misprediction(self, instruction):
        """Maneja la penalización por predicción incorrecta."""
        print("Predicción incorrecta detectada. Penalización aplicada.")
        self.procesador.clear_pipeline()
        self.procesador.PC -= instruction.offset + 1  # Penalización por mal predicción

    def check_forwarding(self, current_instruction):
        """Verifica y aplica forwarding para instrucciones que usan registros."""
        if not isinstance(current_instruction, (Add, Sub, Or, And)):
            print("No se aplica forwarding: instrucción no es de tipo Add.")
            return  # Por ahora, solo procesamos instrucciones tipo Add

        # Asegurarse de que regRF.data sea una lista inicializada
        if current_instruction.procesador.regRF.data is None:
            current_instruction.procesador.regRF.data = [None, None]

        # Bandera para detectar si hubo forwarding
        forwarding_applied = False

        # Forwarding desde ALU
        if self.procesador.regALU.instruccion:
            alu_inst = self.procesador.regALU.instruccion
            if hasattr(alu_inst, 'destino') and alu_inst.destino == current_instruction.registro1:
                print(f"Forwarding desde ALU a DECODE para registro {current_instruction.registro1}.")
                current_instruction.procesador.regRF.data[0] = self.procesador.regALU.data
                forwarding_applied = True
            if hasattr(alu_inst, 'destino') and alu_inst.destino == current_instruction.registro2:
                print(f"Forwarding desde ALU a DECODE para registro {current_instruction.registro2}.")
                current_instruction.procesador.regRF.data[1] = self.procesador.regALU.data
                forwarding_applied = True

        # Forwarding desde MEM
        if self.procesador.regDM.instruccion:
            dm_inst = self.procesador.regDM.instruccion
            if hasattr(dm_inst, 'destino') and dm_inst.destino == current_instruction.registro1:
                print(f"Forwarding desde MEM a DECODE para registro {current_instruction.registro1}.")
                current_instruction.procesador.regRF.data[0] = self.procesador.RF.registros[dm_inst.destino]
                forwarding_applied = True
            if hasattr(dm_inst, 'destino') and dm_inst.destino == current_instruction.registro2:
                print(f"Forwarding desde MEM a DECODE para registro {current_instruction.registro2}.")
                current_instruction.procesador.regRF.data[1] = self.procesador.RF.registros[dm_inst.destino]
                forwarding_applied = True

        # Mensaje si no hubo forwarding
        if not forwarding_applied:
            print("No hubo necesidad de aplicar forwarding para esta instrucción.")

    def forward_from_execute(self, destino, resultado):
        """Envía el resultado de ALU al registro correspondiente."""
        print(f"Forwarding directo desde EXECUTE al destino R{destino}")
        # Actualiza el valor en el archivo de registros
        self.procesador.RF.registros[destino] = resultado

        # Si no hay instrucción en DECODE, no es necesario imprimir mensajes adicionales
        if not self.procesador.regRF.instruccion:
            return

        # Bandera para detectar si hubo forwarding
        forwarding_applied = False

        # Si hay instrucciones esperando este valor, lo forwardea a ellas
        inst = self.procesador.regRF.instruccion
        if isinstance(inst, (Add, Sub, Or, And)):
            if inst.registro1 == destino and self.procesador.regRF.data[0] is None:
                print(f"Forwarding R{destino} a registro1 en DECODE.")
                self.procesador.regRF.data[0] = resultado
                forwarding_applied = True
            if inst.registro2 == destino and self.procesador.regRF.data[1] is None:
                print(f"Forwarding R{destino} a registro2 en DECODE.")
                self.procesador.regRF.data[1] = resultado
                forwarding_applied = True

        # Mensaje si no hubo necesidad de aplicar forwarding
        if not forwarding_applied:
            print(f"No hubo necesidad de aplicar forwarding desde EXECUTE para el destino R{destino}.")

class BranchPredictor:
    def __init__(self, default_prediction=False):
        """
        Inicializa el BranchPredictor con una política predeterminada.
        default_prediction: True para 'salto tomado', False para 'no tomado'.
        """
        self.history = {}  # Diccionario con el historial dinámico
        self.default_prediction = default_prediction  # Política predeterminada

    def predict(self, instruction_id):
        """Devuelve la predicción para una instrucción específica."""
        # Si no hay historial, aplica la predicción por defecto
        return self.history.get(instruction_id, self.default_prediction)

    def update(self, instruction_id, actual_outcome):
        """Actualiza el historial dinámico basado en el resultado real."""
        self.history[instruction_id] = actual_outcome
        print(f"Historial actualizado para instrucción {instruction_id}: {actual_outcome}")

    def reset(self):
        """Resetea el historial dinámico."""
        self.history = {}
