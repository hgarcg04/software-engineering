from src.modelo.VO.PacientesVO import PacientesVO

class ControladorAdministrativos:
    def __init__(self, vista, modelo, user_vo):
        self._vista = vista
        self._modelo = modelo
        self.user_vo = user_vo

    def cerrar_sesion(self):
        self._vista.signal_logout.emit()

    def registrar_paciente(self, nif, nombre, apellido1, apellido2, fecha_nacimiento, genero, correo, direccion, alergias, telefono):
        pacienteVO = PacientesVO(nif=nif, nombre=nombre,
                                apellido1=apellido1,
                                apellido2=apellido2,
                                fecha_nacimiento=fecha_nacimiento,
                                genero=genero,
                                correo = correo,
                                direccion = direccion,
                                alergias = alergias,
                                telefono = telefono)
        return self._modelo.registrarPaciente(pacienteVO)