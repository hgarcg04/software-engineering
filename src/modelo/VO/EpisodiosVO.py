class EpisodioVO:
    def __init__(self, id_paciente, id_medico, diagnostico,
                tipo, id_episodio, fecha_hora_inicio, med_apellidos,
                fecha_hora_fin=None, sintomas=None):
        self.id_paciente = id_paciente
        self.id_medico = id_medico
        self.sintomas = sintomas
        self.diagnostico = diagnostico
        self.tipo = tipo
        self.id_episodio = id_episodio
        self.fecha_hora_inicio = fecha_hora_inicio
        self.fecha_hora_fin = fecha_hora_fin
        self.med_apellidos = med_apellidos
      


