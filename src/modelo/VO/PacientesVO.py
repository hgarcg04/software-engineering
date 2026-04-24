class PacientesVO:
    def __init__(self, nif, nombre, apellido1, apellido2,
                 fecha_nacimiento, genero, fecha_registro,
                 medico_asignado):
        
        self.nif = nif
        self.nombre = nombre
        self.apellido1 = apellido1
        self.apellido2 = apellido2
        self.fecha_nacimiento = fecha_nacimiento
        self.genero = genero
        self.fecha_registro = fecha_registro
        self.medico_asignado = medico_asignado

