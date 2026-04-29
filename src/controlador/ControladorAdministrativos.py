class ControladorAdministrativos:
    def __init__(self, vista, modelo, user_vo):
        self._vista = vista
        self._modelo = modelo
        self.user_vo = user_vo

    def cerrar_sesion(self):
        self._vista.signal_logout.emit()