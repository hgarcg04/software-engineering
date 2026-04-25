class PacientesVO:
    def __init__(self, id_episodio, nif, nombre, apellido1, apellido2,
                 fecha_nacimiento, genero, fecha_registro,
                 medico_asignado, num_habitacion=None, fecha_ingreso=None,
                 dieta=None):
        
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
        self.fecha_ingreso = fecha_ingreso
        self.dieta = dieta
    
    @property

    def nombre_completo(self):
        apellidos = f"{self.apellido1} {self.apellido2}".strip()
        return f"{apellidos}, {self.nombre}"

    