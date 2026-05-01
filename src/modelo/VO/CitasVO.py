class CitaVO:
    def __init__(self, id_cita, id_medico, id_paciente, fecha, hora, motivo, paciente_nombre):
        self.id_cita = id_cita
        self.id_medico = id_medico
        self.id_paciente = id_paciente
        self.fecha = fecha
        self.hora = hora
        self.motivo = motivo
        self.paciente_nombre = paciente_nombre