# Mixin de vista para CU4 (Asignar Citas) y CU9 (Bloquear Agenda).
# VentanaAdministrativos hereda de esta clase.

from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem
from PyQt5.QtCore import QDate, Qt
from src.vista.Administrativos.LogicaDialogoCalendario import DialogCalendario

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

        #Asignar Citas
        # Filtrado en tiempo real al escribir en el buscador
        self.search_bar.textChanged.connect(self._on_texto_busqueda_cambiado)
        self.tabla_pacientes_cita.itemSelectionChanged.connect(self._on_paciente_seleccionado)
        self.btn_deseleccionar.clicked.connect(self._on_deseleccionar_paciente)
        self.btn_paciente_no_encontrado.clicked.connect(self._on_paciente_no_encontrado)
        self.btn_paciente_no_encontrado.setVisible(False)
        self.combo_especialidad.currentIndexChanged.connect(self._on_especialidad_cambiada)
        # IMPORTANTE: combo_medico_cita NO conecta a limpiar_horas para no
        # borrar las horas cargadas nada más seleccionar médico
        self.btn_consultar_disponibilidad.clicked.connect(self._on_abrir_calendario)
        #print(f"_init_citas llamado")
        self.btn_asignar_cita.clicked.connect(self._on_asignar_cita)
        self.btn_limpiar_cita.clicked.connect(self._on_limpiar_cita)

        #Bloquear Agenda
        manana = QDate.currentDate().addDays(1)
        self.input_fecha_inicio_bloqueo.setDate(manana)
        self.input_fecha_fin_bloqueo.setDate(manana)
        self.search_medico.textChanged.connect(self._on_texto_medico_cambiado)
        self.btn_buscar_medico.clicked.connect(self._on_buscar_medico)
        self.tabla_medicos_agenda.itemSelectionChanged.connect(self._on_medico_agenda_seleccionado)
        self.btn_deseleccionar_medico.clicked.connect(self._on_deseleccionar_medico)
        self.btn_bloquear_agenda.clicked.connect(self._on_bloquear_agenda)


    #Asignar Citas

    def _on_texto_busqueda_cambiado(self, texto):
        """Delega el filtrado al controlador cada vez que cambia el texto."""
        if self._controlador:
            self._controlador.filtrar_pacientes(texto)

    def _on_paciente_no_encontrado(self):
        """El controlador decide la redirección; la vista solo captura el evento."""
        if self._controlador:
            self._controlador.ir_a_registro_paciente()

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

    def _on_abrir_calendario(self):
        """Abre el diálogo de calendario semanal para elegir fecha y hora."""
        id_medico = self.combo_medico_cita.currentData()
        if not id_medico:
            QMessageBox.warning(self, "Sin médico", "Selecciona un médico primero.")
            return
        if self._controlador:
            fecha = self.input_fecha_cita.date().toPyDate()
            self._controlador.abrir_calendario(id_medico, fecha)

    def _on_asignar_cita(self):
        id_medico = self.combo_medico_cita.currentData()
        hora = self.combo_hora_cita.currentData()
        fecha = self.input_fecha_cita.date().toPyDate()
        if self._controlador:
            self._controlador.asignar_cita(id_medico, fecha, hora)

    #Métodos llamados por el controlador

    def abrir_calendario_dialogo(self, id_medico, nombre_medico, fn_citas, fn_bloqueados, fecha_inicial=None):
        """
        Instancia y abre el DialogCalendario modal.
        Cuando el usuario elige una celda libre, rellena fecha y hora en el formulario.
        """
        dialogo = DialogCalendario(
            id_medico, nombre_medico,
            fn_citas=fn_citas,
            fn_bloqueados=fn_bloqueados,
            fecha_inicial=fecha_inicial,
            parent=self
        )
        dialogo.hora_seleccionada.connect(self._on_hora_desde_calendario, Qt.UniqueConnection)
        dialogo.exec_()

    def _on_hora_desde_calendario(self, fecha, hora):
        """Recibe fecha y hora del calendario y las vuelca en los widgets del formulario."""
        from PyQt5.QtCore import QDate
        self.input_fecha_cita.setDate(QDate(fecha.year, fecha.month, fecha.day))
        # Cargar la hora directamente en el combo
        self.combo_hora_cita.clear()
        self.combo_hora_cita.addItem(hora, hora)
        self.btn_asignar_cita.setEnabled(True)

    def _on_limpiar_cita(self):
        if self._controlador:
            self._controlador.limpiar_formulario_cita()

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
        """Actualiza el nombre en el frame; el frame siempre es visible."""
        self.lbl_paciente_sel_nombre.setText(nombre_completo)

    def limpiar_seleccion_paciente(self):
        """Resetea el nombre a 'Ninguno' sin ocultar el frame ni el botón deseleccionar."""
        self.lbl_paciente_sel_nombre.setText("Ninguno")
        self.tabla_pacientes_cita.setRowCount(0)
        self.search_bar.clear()

    def mostrar_btn_no_encontrado(self, visible):
        """Muestra u oculta el botón de paciente no encontrado según el resultado."""
        self.btn_paciente_no_encontrado.setVisible(visible)

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
        self._limpiar_todo_citas()

    def _limpiar_todo_citas(self):
        """Resetea todos los campos de la pestaña de citas a su estado inicial."""
        self.limpiar_seleccion_paciente()
        self.limpiar_horas()
        self.combo_especialidad.setCurrentIndex(0)
        self.combo_medico_cita.setCurrentIndex(0)
        self.input_fecha_cita.setDate(__import__('PyQt5.QtCore', fromlist=['QDate']).QDate.currentDate())
        self.btn_asignar_cita.setEnabled(False)
        self.btn_paciente_no_encontrado.setVisible(False)

    def navegar_a_registro(self):
        """Llamado por el controlador para ir a la pestaña de registro de paciente."""
        self._navegar(PAGE_PACIENTES)

    #Bloquear Agenda

    def _on_texto_medico_cambiado(self, texto):
        """Filtra la tabla de médicos en tiempo real mientras el usuario escribe."""
        if self._controlador:
            self._controlador.filtrar_medicos_agenda(texto)

    def _on_buscar_medico(self):
        texto = self.search_medico.text().strip()
        if self._controlador:
            self._controlador.buscar_medico_agenda(texto)

    def _on_medico_agenda_seleccionado(self):
        fila = self.tabla_medicos_agenda.currentRow()
        if fila >= 0 and self._controlador:
            self._controlador.seleccionar_medico_agenda(fila)

    def _on_deseleccionar_medico(self):
        if self._controlador:
            self._controlador.deseleccionar_medico_agenda()

    def _on_bloquear_agenda(self):
        fecha_inicio = self.input_fecha_inicio_bloqueo.date().toPyDate()
        fecha_fin = self.input_fecha_fin_bloqueo.date().toPyDate()
        motivo = self.combo_motivo_bloqueo.currentText()
        observaciones = self.input_observaciones_bloqueo.text().strip()
        if self._controlador:
            self._controlador.bloquear_agenda(fecha_inicio, fecha_fin, motivo, observaciones)

    #Métodos llamados por el controlador

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
        self.btn_deseleccionar_medico.setVisible(True)

    def limpiar_seleccion_medico(self):
        """Resetea solo la selección de médico; mantiene tabla y buscador intactos."""
        self.lbl_medico_sel_nombre.setText("Ninguno")
        self.btn_deseleccionar_medico.setVisible(False)

    def confirmar_agenda_bloqueada(self):
        QMessageBox.information(self, "Agenda bloqueada", "Las fechas han sido bloqueadas correctamente.")
        manana = QDate.currentDate().addDays(1)
        self.lbl_medico_sel_nombre.setText("Ninguno")
        self.btn_deseleccionar_medico.setVisible(False)
        self.input_observaciones_bloqueo.clear()
        self.input_fecha_inicio_bloqueo.setDate(manana)
        self.input_fecha_fin_bloqueo.setDate(manana)

    def limpiar_formulario_cita(self):
        self._limpiar_todo_citas()


    # ── Utilidades ────────────────────────────────────────────────────────────

    def mostrar_error(self, titulo, mensaje):
        QMessageBox.warning(self, titulo, mensaje)

    def mostrar_info(self, titulo, mensaje):
        QMessageBox.information(self, titulo, mensaje)

    def _item(self, texto):
        return QTableWidgetItem(str(texto))