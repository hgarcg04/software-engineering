class ConstantesVO:
     def __init__(self, tipo, valor, observaciones, id_enfermero, id_ingreso, nif_paciente=None, id_episodio=None, fecha=None, hora=None):
        self.tipo = tipo
        self.valor = valor
        self.observaciones = observaciones
        self.id_enfermero = id_enfermero
        self.nif_paciente = nif_paciente
        self.id_episodio = id_episodio
        self.id_ingreso = id_ingreso
        self.fecha = fecha
        self.hora = hora
