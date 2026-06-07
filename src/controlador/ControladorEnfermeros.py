from src.modelo.VO.ConstantesVO import ConstantesVO
from src.modelo.VO.TomaVO import TomaVO
from src.modelo.VO.MedicamentosVO import MedicamentoVO
from src.modelo.LogicaGraficas import LogicaGraficas
from src.vista.Enfermeros.GeneradorGraficas import LogicaGenerarGrafica
from src.modelo.GeneradorInformePDF import GeneradorInformePDF

class ControladorEnfermeros:
    def __init__(self, vista, modelo, user_vo, controlador_principal=None):
        self._vista = vista
        self._modelo = modelo
        self.user_vo = user_vo
        self.controlador_principal = controlador_principal

        self._paciente_hcd_actual = None
        self._episodios_hcd_actuales = []

        self._cargar_pacientes()

    def _cargar_pacientes(self):
        """
            Método que le pide al modelo, la lista de pacientes ingresados
            asociados al enfermero que esta usando la App (user_vo)
            El modelo devuelve una lista de objetos PacientesVO.
            Finalmente, se usa el método de la logicaEnfermeros para cargar los pacientes.
        """
        lista_pacientes = self._modelo.obtenerPacientes(self.user_vo) or []
        self._vista.cargar_datos_iniciales(lista_pacientes, self.user_vo)

    def cargar_tratamientos(self, pacienteVO):
        """
            Pedimos al modelo un listado de los tratamientos activos del paciente seleccionado.
            Luego mostramos la lista en la vista.
        """
        lista_tratamientos = self._modelo.obtenerTratamientos(pacienteVO)
        if lista_tratamientos:
            self._vista.mostrar_tratamientos(lista_tratamientos)


    def guardar_constante(self, lista_dicts, id_enfermero, id_ingreso):
        """
            Llamamos al metodo del modelo que alamacena cada registro de una nueva constante.
            Lo hacemos para cada elemento de la lista de objetos ConstanteVO.
        """
        print("(Controlador): Recibo la lista de constantes:")
        for c in lista_dicts:
            constanteVO = ConstantesVO(c['tipo'], c['valor'], c.get('observaciones', ''), id_enfermero, id_ingreso)
            print("ID del enfermero: ", constanteVO.id_enfermero)
            self._modelo.guardarConstante(constanteVO)

    
    def set_dialogo_historico(self, dialogo):
        """
            Cambiamos la ref de la vista VentanaEnfermeros -> DialogoHistorico
        """
        self._vista = dialogo

    
    def set_ventana_enfermeros(self, ventana):
        """
            Método para devolver la referencia de la vista a la ventanaEnfermeros
        """
        self._vista = ventana

    def consultar_historico(self, id_episodio, tipo, desde, hasta):
        """
            LLamamo al método del modelo que hace la consulta de las constantes
            en la base de datos, para un rango de tiempo concreto.
        """
        resultados = self._modelo.consultarHistoricoConstantes(id_episodio, tipo, desde, hasta)
        self._vista.cargar_resultados(resultados) # Hacemos que la ventana de dialogo muestre los resultados

    def generar_grafico(self, id_episodio, tipo, desde, hasta):
        modelo = LogicaGraficas()
        vista = LogicaGenerarGrafica()

        datos = modelo.devolver_datos_grafico(id_episodio, tipo, desde, hasta)
        if datos[0] is None:
            print("Datos no encontrado")
            return

        df_constantes, tomas, rangos = datos
        vista.generar_grafico(df_constantes, tomas, rangos, id_episodio, tipo)

    def guardar_nueva_toma(self, id_empleado, id_tratamiento, observaciones):
        tomaVO =TomaVO(id_empleado, id_tratamiento, observaciones)
        self._modelo.guardarNuevaToma(tomaVO)
    
    def obtener_ultima_toma(self, tratamientoVO):
        ultima_toma = self._modelo.obtenerUltimaToma(tratamientoVO)
        self._vista.cargar_ultima_toma(ultima_toma)
    
    def obtener_tomas_sesion_actual(self, pacienteVO):
        tomas_sesion = self._modelo.obtenerTomasSesionActual(pacienteVO)
        self._vista.cargar_tomas_sesion_actual(tomas_sesion)

    def eliminar_toma(self, id_toma):
        self._modelo.eliminarToma(id_toma)

    def actualizar_stock(self, id_medicamento, cantidad):
        medicamentoVO = self._modelo.obtenerMedicamentoPorId(id_medicamento)
        print(medicamentoVO.stock_minimo)
        stock_actual = medicamentoVO.stock + cantidad
        self._modelo.actualizarStock(medicamentoVO.id_medicamento, cantidad)

        if stock_actual < medicamentoVO.stock_minimo:

            self._set_alerta_stock(medicamentoVO.id_medicamento, 1)
            retorno = self._avisar_falta_stock_en_tablon(self.user_vo, f"Stock actual de '{medicamentoVO.nombre}': {stock_actual}"
                                                                             f" (Stock minimo: {medicamentoVO.stock_minimo})")
            if retorno:
                self._vista.confirmar_aviso()

        else:

            self._set_alerta_stock(medicamentoVO.id_medicamento, 0)


    def _set_alerta_stock(self, id_medicamento, bit):
        self._modelo.setAlertaStock(id_medicamento, bit)

    def _avisar_falta_stock_en_tablon(self, usuario, mensaje):
        return self._modelo.agregarTareas(usuario, mensaje)
    

    def cambiar_password(self, nueva, enfermero):
        self.controlador_principal.cambiar_password(nueva, enfermero)

    def crear_pdf_informe(self, parent, ruta, pacVO):
        generador = GeneradorInformePDF()
        generador.crear_pdf_informe(parent, ruta, pacVO)


    # ── HCD ──────────────────────────────────────────────────────

    def buscar_paciente_hcd(self, texto):
        texto_lower = texto.strip().lower()
        filtrados = [
            p for p in self._modelo.obtenerPacientes(self.user_vo) or []
            if texto_lower in p.nif.lower()
                       or texto_lower in p.nombre.lower()
                       or texto_lower in p.apellido1.lower()
                       or texto_lower in p.apellido2.lower()
                       or texto_lower in f"{p.nombre} {p.apellido1} {p.apellido2}".lower()
        ]
        self._vista.cargar_resultados_busqueda_hcd(filtrados)

    def cargar_episodios_hcd(self, pacienteVO):
        self._paciente_hcd_actual = pacienteVO
        episodios = self._modelo.obtenerEpisodios(pacienteVO.id_paciente)
        self._episodios_hcd_actuales = episodios if episodios else []
        self._vista.cargar_episodios_hcd(pacienteVO.nombre_completo, self._episodios_hcd_actuales)

    def cargar_detalle_episodio_hcd(self, fila):
        if fila >= len(self._episodios_hcd_actuales):
            return
        ep = self._episodios_hcd_actuales[fila]
        texto = (
            f"Tipo: {ep.tipo}\n"
            f"Fecha inicio: {ep.fecha_hora_inicio}\n"
            f"Fecha fin: {ep.fecha_hora_fin}\n\n"
            f"Diagnóstico:\n{ep.diagnostico}"
        )
        tratamientos = self._modelo.obtenerTratamientos_por_episodio(ep.id_episodio)
        self._vista.mostrar_detalle_episodio_hcd(texto, tratamientos if tratamientos else [])