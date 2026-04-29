from src.vista.LogicaDialogoReceta import DialogoReceta
from src.modelo.VO.EpisodiosVO import EpisodioVO
from src.modelo.VO.TratamientosVO import TratamientoVO


class ControladorMedicos:
    def __init__(self, vista, modelo, user_vo):
        self._vista = vista
        self._modelo = modelo
        self._user_vo = user_vo
        self._episodios_actuales = []   # cache para el HCD
        self._paciente_hcd_actual = None

        self._vista.cargar_datos_iniciales(self._user_vo)

        self._cargar_agenda_hoy()

    # ── Inicio ───────────────────────────────────────────────────

    def _cargar_agenda_hoy(self):
        """
        Carga las citas del día de hoy para este médico.
        El modelo debe devolver una lista de dicts con:
          hora, paciente, motivo, estado, id_cita, id_paciente
        """
        lista = self._modelo.obtenerAgendaHoy(self._user_vo)
        if lista:
            self._vista.cargar_agenda_hoy(lista)

    # ── Agenda completa ──────────────────────────────────────────

    def cargar_agenda_completa(self, desde=None, hasta=None):
        """
        Carga la agenda del médico filtrada por rango de fechas.
        El modelo debe devolver una lista de dicts con:
          fecha_hora, paciente, motivo, estado
        """
        lista = self._modelo.obtenerAgenda(self._user_vo, desde, hasta)
        self._vista.cargar_agenda_completa(lista if lista else [])

    # ── Consulta ─────────────────────────────────────────────────

    def guardar_consulta(self, sintomas, diagnostico, tipo, cita):
        """
        Guarda el episodio clínico de la consulta.

        Parámetros que recibe guardar_consulta():
          - sintomas   (str)  texto libre con los síntomas
          - diagnostico (str) texto libre con el diagnóstico
          - tipo        (str) 'Consulta' | 'Urgencia' | 'Revisión'
          - cita        (dict) con al menos: id_cita, id_paciente

        El controlador construye el VO y llama al modelo.
        """
        episodioVO = EpisodioVO(
            id_paciente=cita.get('id_paciente'),
            id_medico=self._user_vo.id_empleado,
            sintomas=sintomas,
            diagnostico=diagnostico,
            tipo=tipo,
            id_cita=cita.get('id_cita')
        )
        self._modelo.guardarEpisodio(episodioVO)

    def ingresar_paciente(self, cita):
        """
        Marca al paciente como ingresado.
        Parámetros: cita (dict) con id_paciente.
        """
        self._modelo.ingresarPaciente(cita.get('id_paciente'), self._user_vo.id_empleado)

    # ── Receta ───────────────────────────────────────────────────

    def abrir_receta(self, cita):
        """
        Abre el diálogo de receta pasándole el paciente activo.
        """
        dialogo = DialogoReceta(parent=self._vista, paciente_nombre=cita.get('nombre', ''))
        dialogo.controlador = self
        dialogo.exec_()

    """ def guardar_receta(self, id_medicamento, dosis, frecuencia, via, fecha_inicio, fecha_fin, notas, id_paciente):
        tratamientoVO = TratamientoVO(
            id_tratamiento=None,       # lo asigna la BD
            id_ingreso=id_ingreso,     # necesitarás pasarlo desde la cita
            id_medico=self._user_vo.id_empleado,
            id_medicamento=id_medicamento,
            dosis=dosis,
            frecuencia=frecuencia,
            notas=notas,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            activo=True,
            via_administracion=via,
            nombre=None,
            categoria=None,
            descripcion=None,
            unidad_medida=None,
            stock=None,
            stock_minimo=None,
            alerta_stock=None
        )
        self._modelo.guardarTratamiento(tratamientoVO)
        """

    # ── HCD ──────────────────────────────────────────────────────

    def buscar_paciente_hcd(self, texto):
        if len(texto) < 2:
            return
        resultados = self._modelo.buscarPaciente(texto)
        self._vista.cargar_resultados_busqueda_hcd(resultados if resultados else [])

    def cargar_detalle_episodio(self, fila):
        if fila >= len(self._episodios_actuales):
            return
        ep = self._episodios_actuales[fila]
        texto = (
            f"Fecha: {ep.get('fecha', '')}\n"
            f"Tipo: {ep.get('tipo', '')}\n"
            f"Síntomas: {ep.get('sintomas', '')}\n"
            f"Diagnóstico: {ep.get('diagnostico', '')}"
        )
        tratamientos = self._modelo.obtenerTratamientos(ep.get('id_episodio'))
        self._vista.mostrar_detalle_episodio(texto, tratamientos if tratamientos else [])
