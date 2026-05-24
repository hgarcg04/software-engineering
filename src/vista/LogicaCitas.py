# Mixin de vista para CU4 (Asignar Citas) y CU9 (Bloquear Agenda).
# VentanaAdministrativos hereda de esta clase.

from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem
from PyQt5.QtCore import QDate

PAGE_PACIENTES = 1


class LogicaCitas:

    def _init_citas(self):
        """
        Conecta los widgets de ambas pestañas.
        Llamar desde __init__ de VentanaAdministrativos.
        """
        self._pacientes_busqueda = []
        self._medicos_busqueda = []

        # Fecha de cita por defecto: hoy
        self.input_fecha_cita.setDate(QDate.currentDate())

        # ── CU4 ──────────────────────────────────────────────────────────────
        self.btn_buscar_paciente.clicked.connect(self._on_buscar_paciente)
        self.tabla_pacientes_cita.itemSelectionChanged.connect(self._on_paciente_seleccionado)
        self.btn_deseleccionar.clicked.connect(self._on_deseleccionar_paciente)
        self.combo_especialidad.currentIndexChanged.connect(self._on_especialidad_cambiada)
        # IMPORTANTE: combo_medico_cita NO conecta a limpiar_horas para no
        # borrar las horas cargadas nada más seleccionar médico
        self.btn_consultar_disponibilidad.clicked.connect(self._on_consultar_disponibilidad)
        self.btn_asignar_cita.clicked.connect(self._on_asignar_cita)

        # ── CU9 ──────────────────────────────────────────────────────────────
        self.btn_buscar_medico.clicked.connect(self._on_buscar_medico)
        self.tabla_medicos_agenda.itemSelectionChanged.connect(self._on_medico_agenda_seleccionado)
        self.btn_bloquear_agenda.clicked.connect(self._on_bloquear_agenda)

    # ═════════════════════════════════════════════════════════════════════════
    # CU4: Asignar Citas — callbacks
    # ═════════════════════════════════════════════════════════════════════════

    def _on_buscar_paciente(self):
        texto = self.search_bar.text().strip()
        if self._controlador:
            self._controlador.buscar_paciente_cita(texto)

    def _on_paciente_seleccionado(self):
        fila = self.tabla_pacientes_cita.currentRow()
        if fila >= 0 and self._controlador:
            self._controlador.seleccionar_paciente(fila)

    def _on_deseleccionar_paciente(self):
        if self._controlador:
            self._controlador.deseleccionar_paciente()

    def _on_especialidad_cambiada(self):
        especialidad = self.combo_especialidad.currentData()
        if self._controlador:
            self._controlador.filtrar_medicos(especialidad)

    def _on_consultar_disponibilidad(self):
        id_medico = self.combo_medico_cita.currentData()
        fecha = self.input_fecha_cita.date().toPyDate()
        if self._controlador:
            self._controlador.consultar_disponibilidad(id_medico, fecha)

    def _on_asignar_cita(self):
        id_medico = self.combo_medico_cita.currentData()
        hora = self.combo_hora_cita.currentData()
        fecha = self.input_fecha_cita.date().toPyDate()
        motivo = self.input_motivo_cita.text().strip()
        if self._controlador:
            self._controlador.asignar_cita(id_medico, fecha, hora, motivo)

    # ── Métodos llamados por el controlador ───────────────────────────────────

    def cargar_especialidades(self, lista_especialidades):
        """Puebla el combo de especialidades."""
        self.combo_especialidad.blockSignals(True)
        self.combo_especialidad.clear()
        self.combo_especialidad.addItem("— Todas las especialidades —", None)
        for esp in lista_especialidades:
            self.combo_especialidad.addItem(esp, esp)
        self.combo_especialidad.blockSignals(False)

    def cargar_medicos(self, lista_medicos):
        """Puebla el combo de médicos y limpia las horas al cambiar la lista."""
        self.combo_medico_cita.blockSignals(True)
        self.combo_medico_cita.clear()
        self.combo_medico_cita.addItem("— Selecciona un médico —", None)
        for m in lista_medicos:
            # m = (id_empleado, nombre, apellidos, especialidad)
            self.combo_medico_cita.addItem(f"{m[2]}, {m[1]}  [{m[3]}]", m[0])
        self.combo_medico_cita.blockSignals(False)
        self.limpiar_horas()

    def cargar_resultados_busqueda_paciente(self, lista_pacientes):
        """
        Rellena tabla_pacientes_cita.
        Columnas del UI: DNI | Paciente | Nº Expediente
        """
        self._pacientes_busqueda = lista_pacientes
        self.tabla_pacientes_cita.setRowCount(0)
        for p in lista_pacientes:
            row = self.tabla_pacientes_cita.rowCount()
            self.tabla_pacientes_cita.insertRow(row)
            self.tabla_pacientes_cita.setItem(row, 0, self._item(p.nif))
            self.tabla_pacientes_cita.setItem(row, 1, self._item(p.nombre_completo))
            self.tabla_pacientes_cita.setItem(row, 2, self._item(str(p.id_paciente)))
        self.tabla_pacientes_cita.resizeColumnsToContents()

    def mostrar_paciente_seleccionado(self, nombre_completo):
        self.lbl_paciente_sel_nombre.setText(nombre_completo)
        self.frame_paciente_seleccionado.setVisible(True)

    def limpiar_seleccion_paciente(self):
        self.lbl_paciente_sel_nombre.setText("")
        self.frame_paciente_seleccionado.setVisible(False)
        self.tabla_pacientes_cita.setRowCount(0)
        self.search_bar.clear()

    def cargar_horas_disponibles(self, lista_horas):
        """
        Rellena el combo de horas. Cada item tiene la hora como data()
        para que currentData() devuelva siempre un string válido.
        Habilita el botón de confirmar cita al tener horas disponibles.
        """
        self.combo_hora_cita.clear()
        for h in lista_horas:
            self.combo_hora_cita.addItem(h, h)
        # Conectar cambio de hora para habilitar el botón de confirmar
        self.combo_hora_cita.currentIndexChanged.connect(self._on_hora_seleccionada)
        self._on_hora_seleccionada()

    def limpiar_horas(self):
        """Resetea el combo de horas y deshabilita el botón de confirmar."""
        self.combo_hora_cita.clear()
        self.combo_hora_cita.addItem("— Consulta disponibilidad —", None)
        self.btn_asignar_cita.setEnabled(False)

    def _on_hora_seleccionada(self):
        """Habilita confirmar cita solo cuando hay una hora real seleccionada."""
        hora = self.combo_hora_cita.currentData()
        self.btn_asignar_cita.setEnabled(hora is not None)

    def confirmar_cita_asignada(self):
        QMessageBox.information(self, "Cita asignada", "La cita se ha asignado correctamente.")
        self.limpiar_seleccion_paciente()
        self.input_motivo_cita.clear()
        self.limpiar_horas()

    def redirigir_a_registro_paciente(self):
        """Ofrece ir a registrar el paciente si no se encuentra en la BD."""
        resp = QMessageBox.question(
            self, "Paciente no encontrado",
            "No se encontró ningún paciente con ese criterio.\n"
            "¿Deseas registrar un nuevo paciente ahora?",
            QMessageBox.Yes | QMessageBox.No
        )
        if resp == QMessageBox.Yes:
            self._navegar(PAGE_PACIENTES)

    # ═════════════════════════════════════════════════════════════════════════
    # CU9: Bloquear Agenda — callbacks
    # ═════════════════════════════════════════════════════════════════════════

    def _on_buscar_medico(self):
        texto = self.search_medico.text().strip()
        if self._controlador:
            self._controlador.buscar_medico_agenda(texto)

    def _on_medico_agenda_seleccionado(self):
        fila = self.tabla_medicos_agenda.currentRow()
        if fila >= 0 and self._controlador:
            self._controlador.seleccionar_medico_agenda(fila)

    def _on_bloquear_agenda(self):
        fecha_inicio = self.input_fecha_inicio_bloqueo.date().toPyDate()
        fecha_fin = self.input_fecha_fin_bloqueo.date().toPyDate()
        motivo = self.combo_motivo_bloqueo.currentText()
        observaciones = self.input_observaciones_bloqueo.text().strip()
        if self._controlador:
            self._controlador.bloquear_agenda(fecha_inicio, fecha_fin, motivo, observaciones)

    # ── Métodos llamados por el controlador ───────────────────────────────────

    def cargar_resultados_busqueda_medico(self, lista_medicos):
        """
        Rellena tabla_medicos_agenda.
        Columnas del UI: ID | Nombre | Especialidad
        """
        self._medicos_busqueda = lista_medicos
        self.tabla_medicos_agenda.setRowCount(0)
        for m in lista_medicos:
            # m = (id_empleado, nombre, apellidos, especialidad)
            row = self.tabla_medicos_agenda.rowCount()
            self.tabla_medicos_agenda.insertRow(row)
            self.tabla_medicos_agenda.setItem(row, 0, self._item(str(m[0])))
            self.tabla_medicos_agenda.setItem(row, 1, self._item(f"{m[2]}, {m[1]}"))
            self.tabla_medicos_agenda.setItem(row, 2, self._item(m[3] or "—"))
        self.tabla_medicos_agenda.resizeColumnsToContents()

    def mostrar_medico_seleccionado(self, nombre_completo):
        self.lbl_medico_sel_nombre.setText(nombre_completo)
        self.frame_medico_seleccionado.setVisible(True)

    def confirmar_agenda_bloqueada(self):
        QMessageBox.information(self, "Agenda bloqueada", "Las fechas han sido bloqueadas correctamente.")
        self.lbl_medico_sel_nombre.setText("")
        self.frame_medico_seleccionado.setVisible(False)
        self.tabla_medicos_agenda.setRowCount(0)
        self.search_medico.clear()
        self.input_observaciones_bloqueo.clear()

    # ── Utilidades ────────────────────────────────────────────────────────────

    def mostrar_error(self, titulo, mensaje):
        QMessageBox.warning(self, titulo, mensaje)

    def mostrar_info(self, titulo, mensaje):
        QMessageBox.information(self, titulo, mensaje)

    def _item(self, texto):
        return QTableWidgetItem(str(texto))