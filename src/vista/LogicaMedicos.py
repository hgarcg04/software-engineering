import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import pyqtSignal
from PyQt5 import uic
from PyQt5.QtCore import QTimer, QDateTime
from PyQt5.QtWidgets import QButtonGroup

from datetime import datetime, timedelta

from src.vista.LogicaDialogoReceta import DialogoReceta

ui_path = os.path.join(os.path.dirname(__file__), "Ui/VistaMedico.ui")
Form, Window = uic.loadUiType(ui_path)


class VentanaMedico(QMainWindow, Form):
    signal_logout = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._pacientes_busqueda = []
        self.setupUi(self)
        self._controlador = None
        self._cita_activa = None   # dict con los datos de la cita seleccionada
        self._citas_agenda_hoy = {}

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._actualizar_fecha_hora)
        self.timer.start(1000)
        self._actualizar_fecha_hora()

        self._btn_group = QButtonGroup(self)
        self._btn_group.setExclusive(True)
        self._btn_group.addButton(self.btn_nav_inicio)
        self._btn_group.addButton(self.btn_nav_agenda)
        self._btn_group.addButton(self.btn_nav_hcd)

        # --- Navegación sidebar ---
        self.btn_nav_inicio.clicked.connect(self._ir_inicio)
        self.btn_nav_agenda.clicked.connect(self._ir_agenda)
        self.btn_nav_hcd.clicked.connect(self._ir_hcd)

        # --- Inicio: selección de cita ---
        self.tabla_agenda_hoy.itemSelectionChanged.connect(self._on_cita_seleccionada)
        self.btn_iniciar_consulta.clicked.connect(self._abrir_consulta)
        self.btn_ver_hcd_inicio.clicked.connect(self._ver_hcd_paciente_agenda)

        # --- Consulta ---
        self.btn_volver_consulta.clicked.connect(self._ir_inicio)
        self.btn_abrir_receta.clicked.connect(self._abrir_dialogo_receta)
        self.btn_guardar_consulta.clicked.connect(self._guardar_consulta)
        self.btn_ingresar_paciente.clicked.connect(self._ingresar_paciente)

        # --- Agenda completa ---
        self.btn_buscar_agenda.clicked.connect(self._buscar_agenda)

        # --- HCD ---
        self.search_bar.textChanged.connect(self._buscar_paciente_hcd)
        self.tabla_episodios_hcd.itemSelectionChanged.connect(self._on_episodio_seleccionado)
        self.btn_cerrar_detalle.clicked.connect(self._cerrar_detalle_hcd)

        # --- Logout ---
        self.btn_logout.clicked.connect(self._logout)

        self.tabla_busqueda_hcd.itemSelectionChanged.connect(self._on_paciente_hcd_seleccionado)

    # ── Navegación ──────────────────────────────────────────────

    def _ir_inicio(self):
        self.stackedPanel.setCurrentIndex(0)
        self._marcar_nav(self.btn_nav_inicio)

    def _ir_agenda(self):
        self.stackedPanel.setCurrentIndex(1)
        self._marcar_nav(self.btn_nav_agenda)
        if self._controlador:
            self._controlador.cargar_agenda_completa()

    def _ir_hcd(self):
        self.stackedPanel.setCurrentIndex(2)
        self._marcar_nav(self.btn_nav_hcd)

    def _marcar_nav(self, boton_activo):
        for btn in [self.btn_nav_inicio, self.btn_nav_agenda, self.btn_nav_hcd]:
            btn.setChecked(btn == boton_activo)

    # ── Inicio ───────────────────────────────────────────────────

    def cargar_agenda_hoy(self, lista_citas):

        self.tabla_agenda_hoy.setRowCount(0)
        self._citas_agenda_hoy = {}

        # Generar todos los slots de 08:00 a 20:00 cada 30 min
        inicio = datetime.strptime("08:00", "%H:%M")
        fin = datetime.strptime("20:00", "%H:%M")
        slots = []
        actual = inicio
        while actual < fin:
            slots.append(actual.strftime("%H:%M"))
            actual += timedelta(minutes=30)

        # Crear dict hora -> cita usando solo HH:MM
        for cita in lista_citas:
            hora_clave = str(cita['hora'])[:5]
            self._citas_agenda_hoy[hora_clave] = cita

        # Rellenar la tabla con todos los slots
        for slot in slots:
            row = self.tabla_agenda_hoy.rowCount()
            self.tabla_agenda_hoy.insertRow(row)
            self.tabla_agenda_hoy.setItem(row, 0, self._item(slot))
            if slot in self._citas_agenda_hoy:
                cita = self._citas_agenda_hoy[slot]
                self.tabla_agenda_hoy.setItem(row, 1, self._item(cita.get('paciente', '')))
                self.tabla_agenda_hoy.setItem(row, 2, self._item(cita.get('motivo', '')))
            else:
                self.tabla_agenda_hoy.setItem(row, 1, self._item(''))
                self.tabla_agenda_hoy.setItem(row, 2, self._item(''))

        self.tabla_agenda_hoy.resizeColumnsToContents()

    def _on_cita_seleccionada(self):
        filas = self.tabla_agenda_hoy.selectedItems()
        tiene = len(filas) > 0
        self.btn_iniciar_consulta.setEnabled(tiene)
        self.btn_ver_hcd_inicio.setEnabled(tiene)

    def _abrir_consulta(self):
        fila = self.tabla_agenda_hoy.currentRow()
        if fila < 0:
            return
        self._cita_activa = {
            'nombre':  self.tabla_agenda_hoy.item(fila, 1).text(),
            'hora':    self.tabla_agenda_hoy.item(fila, 0).text(),
            'motivo':  self.tabla_agenda_hoy.item(fila, 2).text(),
        }
        self.lbl_cita_nombre.setText(self._cita_activa['nombre'])
        self.lbl_cita_hora.setText(self._cita_activa['hora'])
        self.lbl_cita_motivo.setText(self._cita_activa['motivo'])
        self.edit_sintomas.clear()
        self.edit_diagnostico.clear()
        self.stackedPanel.setCurrentIndex(3)
        self._marcar_nav(None)

    # ── Consulta ─────────────────────────────────────────────────

    def _abrir_dialogo_receta(self):
        if self._controlador:
            self._controlador.abrir_receta(self._cita_activa)

    def _guardar_consulta(self):
        if self._controlador:
            self._controlador.guardar_consulta(
                sintomas=self.edit_sintomas.toPlainText(),
                diagnostico=self.edit_diagnostico.toPlainText(),
                tipo=self.combo_tipo_episodio.currentText(),
                cita=self._cita_activa
            )

    def _ingresar_paciente(self):
        if self._controlador:
            self._controlador.ingresar_paciente(self._cita_activa)

    # ── Agenda completa ──────────────────────────────────────────

    def _buscar_agenda(self):
        if self._controlador:
            self._controlador.cargar_agenda_completa(
                desde=self.date_desde.date().toString('yyyy-MM-dd'),
                hasta=self.date_hasta.date().toString('yyyy-MM-dd')
            )

    def cargar_agenda_completa(self, lista_citas):
        self.tabla_agenda.setRowCount(0)
        for cita in lista_citas:
            row = self.tabla_agenda.rowCount()
            self.tabla_agenda.insertRow(row)
            self.tabla_agenda.setItem(row, 0, self._item(cita.get('fecha_hora', '')))
            self.tabla_agenda.setItem(row, 1, self._item(cita.get('paciente', '')))
            self.tabla_agenda.setItem(row, 2, self._item(cita.get('motivo', '')))
            self.tabla_agenda.setItem(row, 3, self._item(cita.get('estado', '')))
        self.tabla_agenda.resizeColumnsToContents()

    # ── HCD ──────────────────────────────────────────────────────

    def _buscar_paciente_hcd(self, texto):
        if self._controlador:
            self._controlador.buscar_paciente_hcd(texto)

    def cargar_episodios_hcd(self, paciente_nombre, lista_episodios):
        self.lbl_paciente_sel_nombre.setText(paciente_nombre)
        self.tabla_episodios_hcd.setRowCount(0)
        for ep in lista_episodios:
            row = self.tabla_episodios_hcd.rowCount()
            self.tabla_episodios_hcd.insertRow(row)
            self.tabla_episodios_hcd.setItem(row, 0, self._item(ep.get('fecha', '')))
            self.tabla_episodios_hcd.setItem(row, 1, self._item(ep.get('tipo', '')))
            self.tabla_episodios_hcd.setItem(row, 2, self._item(ep.get('diagnostico', '')))
        self.tabla_episodios_hcd.resizeColumnsToContents()

    def _on_episodio_seleccionado(self):
        fila = self.tabla_episodios_hcd.currentRow()
        if fila < 0 or not self._controlador:
            return
        self._controlador.cargar_detalle_episodio(fila)

    def mostrar_detalle_episodio(self, texto, lista_tratamientos):
        self.txt_detalle_episodio.setPlainText(texto)
        self.tabla_tratamientos_hcd.setRowCount(0)
        for t in lista_tratamientos:
            row = self.tabla_tratamientos_hcd.rowCount()
            self.tabla_tratamientos_hcd.insertRow(row)
            self.tabla_tratamientos_hcd.setItem(row, 0, self._item(t.get('medicamento', '')))
            self.tabla_tratamientos_hcd.setItem(row, 1, self._item(t.get('dosis', '')))
            self.tabla_tratamientos_hcd.setItem(row, 2, self._item(t.get('frecuencia', '')))
            self.tabla_tratamientos_hcd.setItem(row, 3, self._item(t.get('via', '')))
        self.tabla_tratamientos_hcd.resizeColumnsToContents()

    def _cerrar_detalle_hcd(self):
        self.txt_detalle_episodio.clear()
        self.tabla_tratamientos_hcd.setRowCount(0)

    # ── Logout ───────────────────────────────────────────────────

    def _logout(self):
        print("Cerrando sesión...")
        self.signal_logout.emit()
        self.close()

    # ── Utilidades ───────────────────────────────────────────────

    def _item(self, texto):
        from PyQt5.QtWidgets import QTableWidgetItem
        return QTableWidgetItem(str(texto))
    
    def _actualizar_fecha_hora(self):
        from PyQt5.QtCore import QDateTime
        self.lbl_datetime.setText(QDateTime.currentDateTime().toString("dd/MM/yyyy  HH:mm"))

    def cargar_datos_iniciales(self, userVO):
        self.lbl_user_name.setText(f"Dr./Dra.: {userVO.nombre} {userVO.apellidos}")

    def cargar_resultados_busqueda_hcd(self, lista_pacientes):
        self._pacientes_busqueda = lista_pacientes
        self.tabla_busqueda_hcd.setRowCount(0)
        for paciente in lista_pacientes:
            row = self.tabla_busqueda_hcd.rowCount()
            self.tabla_busqueda_hcd.insertRow(row)
            self.tabla_busqueda_hcd.setItem(row, 0, self._item(paciente.nif))
            self.tabla_busqueda_hcd.setItem(row, 1, self._item(paciente.nombre_completo))
            self.tabla_busqueda_hcd.setItem(row, 2, self._item(str(paciente.fecha_nacimiento)))
        self.tabla_busqueda_hcd.resizeColumnsToContents()

    def _on_paciente_hcd_seleccionado(self):
        fila = self.tabla_busqueda_hcd.currentRow()
        if fila < 0 or not self._controlador:
            return
        paciente = self._pacientes_busqueda[fila]
        self._controlador.cargar_episodios_paciente(paciente)

    def _ver_hcd_paciente_agenda(self):
        fila = self.tabla_agenda_hoy.currentRow()
        print(f"Fila seleccionada: {fila}")
        if fila < 0:
            return
        hora = self.tabla_agenda_hoy.item(fila, 0).text()[:5]
        print(f"Hora: {hora}")
        print(f"Citas disponibles: {self._citas_agenda_hoy}")
        if hora not in self._citas_agenda_hoy:
            print("Hora no encontrada en citas")
            return
        cita = self._citas_agenda_hoy[hora]
        print(f"Cita encontrada: {cita}")
        self._ir_hcd()
        if self._controlador:
            self._controlador.cargar_hcd_desde_agenda(cita['id_paciente'])

    def abrir_receta(self, cita):
        print("Cita recibida:", cita)
        dialogo = DialogoReceta(parent=self._vista, paciente_vo=None)
        dialogo.lbl_pac_nombre.setText(cita.get('paciente', ''))
        dialogo.controlador = self
        dialogo.exec_()

    @property
    def controlador(self):
        return self._controlador

    @controlador.setter
    def controlador(self, ref):
        self._controlador = ref
