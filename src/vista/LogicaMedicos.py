import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import pyqtSignal, QTimer, QDateTime, QDate
from PyQt5.QtWidgets import QButtonGroup, QTableWidgetItem
from PyQt5 import uic
from datetime import datetime, timedelta
from PyQt5.QtGui import QColor


ui_path = os.path.join(os.path.dirname(__file__), "Ui/VistaMedico.ui")
Form, Window = uic.loadUiType(ui_path)


class VentanaMedico(QMainWindow, Form):
    signal_logout = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._pacientes_busqueda = []
        self._citas_agenda_hoy = {}
        self._cita_activa = None
        self._controlador = None

        self.setupUi(self)

        # Reloj
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._actualizar_fecha_hora)
        self.timer.start(1000)
        self._actualizar_fecha_hora()

        # Botones de navegación exclusivos
        self._btn_group = QButtonGroup(self)
        self._btn_group.setExclusive(True)
        self._btn_group.addButton(self.btn_nav_inicio)
        self._btn_group.addButton(self.btn_nav_agenda)
        self._btn_group.addButton(self.btn_nav_hcd)

        # Navegación sidebar
        self.btn_nav_inicio.clicked.connect(self._ir_inicio)
        self.btn_nav_agenda.clicked.connect(self._ir_agenda)
        self.btn_nav_hcd.clicked.connect(self._ir_hcd)

        # Inicio
        self.tabla_agenda_hoy.itemSelectionChanged.connect(self._on_cita_seleccionada)
        self.btn_iniciar_consulta.clicked.connect(self._abrir_consulta)
        self.btn_ver_hcd_inicio.clicked.connect(self._ver_hcd_paciente_agenda)

        # Consulta
        self.btn_volver_consulta.clicked.connect(self._ir_inicio)
        self.btn_abrir_receta.clicked.connect(self._abrir_dialogo_receta)
        self.btn_guardar_consulta.clicked.connect(self._guardar_consulta)
        self.btn_ingresar_paciente.clicked.connect(self._ingresar_paciente)

        # Agenda completa
        self.btn_buscar_agenda.clicked.connect(self._buscar_agenda)

        # HCD
        self.search_bar.textChanged.connect(self._buscar_paciente_hcd)
        self.tabla_busqueda_hcd.itemSelectionChanged.connect(self._on_paciente_hcd_seleccionado)
        self.tabla_episodios_hcd.itemSelectionChanged.connect(self._on_episodio_seleccionado)
        self.btn_cerrar_detalle.clicked.connect(self._cerrar_detalle_hcd)

        # Logout
        self.btn_logout.clicked.connect(self._logout)

    # ── Navegación ──────────────────────────────────────────────

    def _ir_inicio(self):
        self.stackedPanel.setCurrentIndex(0)
        self.btn_nav_inicio.setChecked(True)

    def _ir_agenda(self):
        self.stackedPanel.setCurrentIndex(1)
        self.btn_nav_agenda.setChecked(True)
        if self._controlador:
            self._controlador.cargar_agenda_completa()

    def _ir_hcd(self):
        self.stackedPanel.setCurrentIndex(2)
        self.btn_nav_hcd.setChecked(True)

    # ── Inicio ───────────────────────────────────────────────────

    def cargar_datos_iniciales(self, userVO):
        self.lbl_user_name.setText(f"Dr./Dra.: {userVO.nombre} {userVO.apellidos}")

    def _actualizar_fecha_hora(self):
        self.lbl_datetime.setText(QDateTime.currentDateTime().toString("dd/MM/yyyy  HH:mm"))

    def establecer_rango_fechas_interfaz(self, fecha_desde_str, fecha_hasta_str):
        # Convertimos los strings que vienen del controlador a objetos QDate
        q_desde = QDate.fromString(fecha_desde_str, "yyyy-MM-dd")
        q_hasta = QDate.fromString(fecha_hasta_str, "yyyy-MM-dd")
        
        # Los widgets del .ui se llaman date_desde y date_hasta
        self.date_desde.setDate(q_desde)
        self.date_hasta.setDate(q_hasta)

    def cargar_agenda_hoy(self, lista_citas):
        self.tabla_agenda_hoy.setRowCount(0)
        self._citas_agendas_hoy = {} # Por si coincide que se pasa de día y no se reinicia, te imaginas? que guapo
        self.tabla_agenda_hoy.verticalHeader().setDefaultSectionSize(45) # Para establecer la altura de las filas
        self.tabla_agenda_hoy.verticalHeader().setVisible(False) # Para que no se vea el índice de la fila que no queda bien

        inicio = datetime.strptime("08:00", "%H:%M")
        fin = datetime.strptime("20:00", "%H:%M")
        hora_actual = datetime.now().strftime("%H:%M")
        slots = []
        actual = inicio
        while actual < fin:
            slots.append(actual.strftime("%H:%M"))
            actual += timedelta(minutes=30)

        for cita in lista_citas:
            hora_clave = str(cita.hora)[:5]
            self._citas_agenda_hoy[hora_clave] = cita

        for slot in slots:
            row = self.tabla_agenda_hoy.rowCount()
            self.tabla_agenda_hoy.insertRow(row)
            self.tabla_agenda_hoy.setItem(row, 0, self._item(slot))
            if slot in self._citas_agenda_hoy:
                cita_vo = self._citas_agenda_hoy[slot]
                self.tabla_agenda_hoy.setItem(row, 1, self._item(cita_vo.paciente_nombre))
                self.tabla_agenda_hoy.setItem(row, 2, self._item(cita_vo.motivo if cita.motivo else ""))
                for col in range(3):
                    self.tabla_agenda_hoy.item(row, col).setBackground(
                        __import__('PyQt5.QtGui', fromlist=['QColor']).QColor('#d8f3ed')
                    )
            else:
                self.tabla_agenda_hoy.setItem(row, 1, self._item(''))
                self.tabla_agenda_hoy.setItem(row, 2, self._item(''))

        self.tabla_agenda_hoy.resizeColumnsToContents()

    def _on_cita_seleccionada(self):
        fila = self.tabla_agenda_hoy.currentRow()
        if fila < 0:
            self.btn_iniciar_consulta.setEnabled(False)
            self.btn_ver_hcd_inicio.setEnabled(False)
            return
        hora = self.tabla_agenda_hoy.item(fila, 0).text()[:5]
        tiene_cita = hora in self._citas_agenda_hoy
        self.btn_iniciar_consulta.setEnabled(tiene_cita)
        self.btn_ver_hcd_inicio.setEnabled(tiene_cita)

    def _abrir_consulta(self):
        fila = self.tabla_agenda_hoy.currentRow()
        if fila < 0:
            return
        hora = self.tabla_agenda_hoy.item(fila, 0).text()[:5]
        if hora not in self._citas_agenda_hoy:
            return
        cita = self._citas_agenda_hoy[hora]
        if self._controlador:
            self._controlador.abrir_seleccion_episodio(cita)
        
    def abrir_pagina_consulta(self, cita_vo, episodio_vo=None):
        """
        Llamado por el controlador tras elegir episodio.
        Recibe la cita y opcionalmente el episodio seleccionado.
        """
        self._cita_activa = cita_vo
        self.lbl_cita_nombre.setText(cita_vo.paciente_nombre)
        self.lbl_cita_hora.setText(str(cita_vo.hora)[:5])
        self.lbl_cita_motivo.setText(cita_vo.motivo if cita_vo.motivo else '')

        if episodio_vo:
            # Episodio existente: pre-rellenar el diagnóstico previo como referencia
            self.edit_sintomas.clear()
            self.edit_diagnostico.setPlainText(
                f"[Continúa episodio del {str(episodio_vo.fecha_hora_inicio)[:10]}]\n"
            )
        else:
            self.edit_sintomas.clear()
            self.edit_diagnostico.clear()

        self.stackedPanel.setCurrentIndex(3)

    def _ver_hcd_paciente_agenda(self):
        fila = self.tabla_agenda_hoy.currentRow()
        if fila < 0:
            return
        hora = self.tabla_agenda_hoy.item(fila, 0).text()[:5]
        if hora not in self._citas_agenda_hoy:
            return
        cita = self._citas_agenda_hoy[hora]
        self._ir_hcd()
        if self._controlador:
            self._controlador.cargar_hcd_desde_agenda(cita.id_paciente)

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
            self.tabla_agenda.setItem(row, 0, self._item(f"{str(cita.fecha)} {str(cita.hora)[:5]}")) # Cambiar esto porque ahora están separados
            self.tabla_agenda.setItem(row, 1, self._item(cita.paciente_nombre))
            self.tabla_agenda.setItem(row, 2, self._item(cita.motivo))
        self.tabla_agenda.resizeColumnsToContents()

    # ── HCD ──────────────────────────────────────────────────────

    def _buscar_paciente_hcd(self, texto):
        if self._controlador:
            self._controlador.buscar_paciente_hcd(texto)

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

    def cargar_episodios_hcd(self, paciente_nombre, lista_episodios):
        self.lbl_paciente_sel_nombre.setText(paciente_nombre)
        self.tabla_episodios_hcd.setRowCount(0)
        for ep in lista_episodios:
            row = self.tabla_episodios_hcd.rowCount()
            self.tabla_episodios_hcd.insertRow(row)
            self.tabla_episodios_hcd.setItem(row, 0, self._item(ep.fecha_hora_inicio))
            self.tabla_episodios_hcd.setItem(row, 1, self._item(ep.tipo))
            self.tabla_episodios_hcd.setItem(row, 2, self._item(ep.diagnostico))
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
        self.signal_logout.emit()
        self.close()

    # ── Utilidades ───────────────────────────────────────────────

    def _item(self, texto):
        from PyQt5.QtWidgets import QTableWidgetItem
        return QTableWidgetItem(str(texto))

    @property
    def controlador(self):
        return self._controlador

    @controlador.setter
    def controlador(self, ref):
        self._controlador = ref
