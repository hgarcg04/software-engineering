class UserVO:
    def __init__(self, id_empleado, dni, nombre, apellidos, email, rol, estado):
        self.id_empleado = id_empleado
        self.rol = rol
        self.nombre = nombre
        self.dni = dni
        self.apellidos = apellidos
        self.email = email
        self.estado = estado
        

    @property
    def nombre_formal_medicos(self):
        if self.rol == 'Medico':
            return f"Dr./Dra {self.apellidos}"
        else:
            raise ValueError("Este atributo solo se usa para los médicos. Usa self.nombre o self.apellidos en su lugar")

