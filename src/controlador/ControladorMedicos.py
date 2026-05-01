from src.vista.LogicaDialogoReceta import DialogoReceta
from src.modelo.VO.EpisodiosVO import EpisodioVO
from src.modelo.VO.TratamientosVO import TratamientoVO
from src.modelo.dao.PacientesDaoJDBC import PacientesDaoJDBC
from src.modelo.VO.CitasVO import CitaVO


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
            id_paciente=cita.id_paciente,
            id_medico=self._user_vo.id_empleado,
            diagnostico=diagnostico,
            tipo=tipo,
            id_episodio=None,           # lo asigna la BD
            fecha_hora_inicio=None,     # lo asigna la BD con GETDATE()
            med_apellidos=self._user_vo.apellidos,
            sintomas=sintomas
        )
    
    def ingresar_paciente(self, cita_vo):
        self._modelo.ingresarPaciente(cita_vo.id_paciente, self._user_vo.id_empleado)

    # ── Receta ───────────────────────────────────────────────────

    def abrir_receta(self, cita):
        print("Paciente en cita:", cita.paciente_nombre)
        dialogo = DialogoReceta(parent=self._vista, paciente_vo=None)
        dialogo.lbl_pac_nombre.setText(cita.paciente_nombre)
        print("Texto puesto en label:", cita.paciente_nombre)
        dialogo._id_paciente = cita.id_paciente
        dialogo.controlador = self
        medicamentos = self._modelo.obtenerMedicamentos()
        # Convertir a lista de dicts para el diálogo
        lista_dicts = [{'id_medicamento': m.id_medicamento, 'nombre': m.nombre,
                        'categoria': m.categoria if m.categoria else '',
                        'stock': m.stock} for m in medicamentos]
        dialogo.cargar_medicamentos(lista_dicts)
        dialogo.exec_() # Puedo cambiar desde aquí la referencia a la vista

    """ def guardar_receta(self, id_medicamento, dosis, frecuencia, via, fecha_inicio, fecha_fin, notas, id_paciente):
        tratamientoVO = TratamientoVO(
            id_tratamiento=None,       # lo asigna la BD
            id_ingreso=None,     # He puesto none porque no es obligatorio
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
            f"Tipo: {ep.tipo}\n"
            f"Fecha inicio: {ep.fecha_hora_inicio}\n"
            f"Fecha fin: {ep.fecha_hora_fin}\n\n"
            f"Diagnóstico:\n{ep.diagnostico}"
        )
        tratamientos = self._modelo.obtenerTratamientos_por_episodio(ep.id_episodio)
        self._vista.mostrar_detalle_episodio(texto, tratamientos if tratamientos else [])
        
    def cargar_episodios_paciente(self, pacienteVO):
        self._paciente_hcd_actual = pacienteVO
        episodios = self._modelo.obtenerEpisodios(pacienteVO.id_paciente)
        self._episodios_actuales = episodios if episodios else []
        self._vista.cargar_episodios_hcd(pacienteVO.nombre_completo, self._episodios_actuales)

    def cargar_hcd_desde_agenda(self, id_paciente):
        dao = PacientesDaoJDBC()
        # Buscamos por id directamente
        pacientes = dao.buscar_paciente_por_id(id_paciente)
        if pacientes:
            self.cargar_episodios_paciente(pacientes[0])