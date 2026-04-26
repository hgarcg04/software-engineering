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
        """
            Llamamos al metodo del modelo que alamacena cada registro de una nueva constante.
            Lo hacemos para cada elemento de la lista de objetos ConstanteVO.
        """
        print("(Controlador): Recibo la lista de constantes:")
        for constanteVO in lista:
            print("ID del enfermero: ", constanteVO.id_enfermero)
            self._modelo.guardarConstante(constanteVO)

    
    def set_dialogo_historico(self, dialogo):
        """
            Cambiamos la ref de la vista VentanaEnfermeros -> DialogoHistorico
        """
        self._vista = dialogo

    def consultar_historico(self, id_episodio, tipo, desde, hasta):
        """
            LLamamo al método del modelo que hace la consulta de las constantes
            en la base de datos, para un rango de tiempo concreto.
        """
        resultados = self._modelo.consultarHistoricoConstantes(id_episodio, tipo, desde, hasta)
        self._vista.cargar_resultados(resultados) # Hacemos que la vista muestre los resultados
    
