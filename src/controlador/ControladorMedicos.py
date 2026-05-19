from src.vista.LogicaDialogoReceta import DialogoReceta
from src.vista.LogicaDialogoEpisodio import DialogoEpisodio
from src.modelo.VO.EpisodiosVO import EpisodioVO
from src.modelo.VO.TratamientosVO import TratamientoVO
from src.modelo.dao.PacientesDaoJDBC import PacientesDaoJDBC
from src.modelo.VO.CitasVO import CitaVO

from datetime import datetime, timedelta


class ControladorMedicos:
    def __init__(self, vista, modelo, user_vo):
        self._vista = vista
        self._modelo = modelo
        self._user_vo = user_vo
        self._episodios_actuales = []
        self._paciente_hcd_actual = None
        self._episodio_consulta_actual = None  # EpisodioVO activo en la consulta

        self._vista.cargar_datos_iniciales(self._user_vo)
        self._cargar_agenda_hoy()

    # ── Inicio ───────────────────────────────────────────────────

    def _cargar_agenda_hoy(self):
        lista = self._modelo.obtenerAgendaHoy(self._user_vo)
        if lista:
            self._vista.cargar_agenda_hoy(lista)

    # ── Agenda completa ──────────────────────────────────────────

    def cargar_agenda_completa(self, desde=None, hasta=None):
        if desde is None:
            desde = datetime.now().strftime('%Y-%m-%d')
        if hasta is None:
            hasta = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        self._vista.establecer_rango_fechas_interfaz(desde, hasta)
        lista = self._modelo.obtenerAgenda(self._user_vo, desde, hasta)
        self._vista.cargar_agenda_completa(lista if lista else [])

    # ── Consulta ─────────────────────────────────────────────────

    def abrir_seleccion_episodio(self, cita_vo): # Llamado por LogicaMedicos._abrir_consulta()
        episodios = self._modelo.obtenerEpisodios(cita_vo.id_paciente)

        dialogo = DialogoEpisodio(
            parent=self._vista,
            paciente_nombre=cita_vo.paciente_nombre,
            episodios=episodios if episodios else []
        )

        if dialogo.exec_() == DialogoEpisodio.Accepted:
            if dialogo.resultado == DialogoEpisodio.EPISODIO_EXISTENTE:
                self._episodio_consulta_actual = dialogo.episodio_seleccionado
            else:
                self._episodio_consulta_actual = None  # nuevo, se creará al guardar

            # Navegar a la página de consulta
            self._vista.abrir_pagina_consulta(cita_vo, self._episodio_consulta_actual)

    def guardar_consulta(self, sintomas, diagnostico, tipo, cita):
        if self._episodio_consulta_actual is not None:
            # Añadir nueva consulta a episodio existente
            self._modelo.guardarConsultaEnEpisodio(
                id_episodio=self._episodio_consulta_actual.id_episodio,
                diagnostico=diagnostico,
                sintomas=sintomas
            )
        else:
            # Crear episodio nuevo con su consulta
            episodioVO = EpisodioVO(
                id_paciente=cita.id_paciente,
                id_medico=self._user_vo.id_empleado,
                diagnostico=diagnostico,
                tipo=tipo,
                id_episodio=None,
                fecha_hora_inicio=None,
                med_apellidos=self._user_vo.apellidos,
                sintomas=sintomas
            )
            self._modelo.guardarEpisodio(episodioVO)

        self._episodio_consulta_actual = None  # resetear tras guardar

    def ingresar_paciente(self, cita_vo):
        self._modelo.ingresarPaciente(cita_vo.id_paciente, self._user_vo.id_empleado)

    # ── Receta ───────────────────────────────────────────────────

    def abrir_receta(self, cita):
        dialogo = DialogoReceta(parent=self._vista, paciente_vo=None)
        dialogo.lbl_pac_nombre.setText(cita.paciente_nombre)
        dialogo._id_paciente = cita.id_paciente
        dialogo.controlador = self
        medicamentos = self._modelo.obtenerMedicamentos()
        dialogo.cargar_medicamentos(medicamentos)
        dialogo.exec_()

    def guardar_receta(self, id_medicamento, dosis, frecuencia, via, fecha_inicio, fecha_fin, notas, id_paciente):
        tratamientoVO = TratamientoVO(
            id_tratamiento=None,
            id_ingreso=None,
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

    # ── HCD ──────────────────────────────────────────────────────

    def buscar_paciente_hcd(self, texto):
        if len(texto) < 2:
            return
        resultados = self._modelo.buscarPaciente(texto)
        self._vista.cargar_resultados_busqueda_hcd(resultados if resultados else [])

    def cargar_episodios_paciente(self, pacienteVO):
        self._paciente_hcd_actual = pacienteVO
        episodios = self._modelo.obtenerEpisodios(pacienteVO.id_paciente)
        self._episodios_actuales = episodios if episodios else []
        self._vista.cargar_episodios_hcd(pacienteVO.nombre_completo, self._episodios_actuales)

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

    def cargar_hcd_desde_agenda(self, id_paciente):
        pacientes = self._modelo.buscarPacientePorId(id_paciente)
        if pacientes:
            self.cargar_episodios_paciente(pacientes[0])
