class ControladorEnfermeros:
    def __init__(self, vista, dao, user_vo):
        self._vista = vista
        self._modelo = dao
        self.user_vo = user_vo

        self._cargar_pacientes()

    def _cargar_pacientes(self):
        """
            Método que le pide al modelo, la lista de pacientes ingresados
            asociados al enfermero que esta usando la App (user_vo)
            El modelo devuelve una lista de objetos PacientesVO.
            Finalmente, se usa el método de la logicaEnfermeros para cargar los pacientes.
        """
        lista_pacientes = self._modelo.obtenerPacientes(self.user_vo)
        if lista_pacientes:
            self._vista.cargar_datos_iniciales(lista_pacientes, self.user_vo)
    
    def guardar_constante(self, lista):
        for constanteVO in lista:
            self._modelo.guardarConstante(constanteVO)
