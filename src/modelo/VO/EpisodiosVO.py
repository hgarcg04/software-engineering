class EpisodioVO:
    def __init__(self, id_paciente, id_medico, sintomas, diagnostico, tipo, id_cita=None):
        self.id_paciente = id_paciente
        self.id_medico = id_medico
        self.sintomas = sintomas
        self.diagnostico = diagnostico
        self.tipo = tipo
        self.id_cita = id_cita