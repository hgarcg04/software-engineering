class PacientesVO:
    def __init__(self, id_episodio, nif, nombre, apellido1, apellido2,
                 fecha_nacimiento, genero, fecha_registro,
                 medico_asignado, num_habitacion=None, fecha_inicio_ep=None,
                 dieta=None, id_ingreso=None, id_paciente=None,
                 fecha_inicio=None, hora_inicio=None, fecha_fin=None,hora_fin=None, observaciones=None): 
        self.id_episodio = id_episodio
        self.nif = nif
        self.nombre = nombre
        self.apellido1 = apellido1
        self.apellido2 = apellido2
        self.fecha_nacimiento = fecha_nacimiento
        self.genero = genero
        self.fecha_registro = fecha_registro
        self.medico_asignado = medico_asignado
        self.num_habitacion = num_habitacion
        self.fecha_inicio_ep = fecha_inicio_ep
        self.dieta = dieta
        self.id_ingreso = id_ingreso
        self.id_paciente = id_paciente
        self.fecha_inicio_ingreso = fecha_inicio
        self.fecha_fin_ingreso = fecha_fin
        self.hora_inicio_ingreso = hora_inicio
        self.hora_fin_ingreso = hora_fin
        self.observaciones = observaciones
    
    @property

    def nombre_completo(self):
        apellidos = f"{self.apellido1} {self.apellido2}".strip()
        return f"{apellidos}, {self.nombre}"

    