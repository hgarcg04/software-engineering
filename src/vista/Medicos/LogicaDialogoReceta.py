import os
from PyQt5.QtWidgets import QDialog, QMessageBox
from PyQt5 import uic
from PyQt5.QtCore import Qt, QDate
from datetime import date, timedelta

ui_path = os.path.join(os.path.dirname(__file__), "../Ui/DialogoReceta.ui")
Form, _ = uic.loadUiType(ui_path)

class DialogoReceta(QDialog, Form):
    def __init__(self, parent, cita_vo):
        super().__init__(parent)
        self.setupUi(self)

        hoy = date.today()
        dentro_de_una_semana = hoy + timedelta(weeks=1)
        self.date_inicio.setDate(QDate(hoy.year, hoy.month, hoy.day))
        self.date_fin.setDate(QDate(dentro_de_una_semana.year, dentro_de_una_semana.month, dentro_de_una_semana.day))

        self._paciente = cita_vo
        self.controlador = None
        self.lbl_pac_nombre.setText('— Sin paciente —')
        self._medicamentos = []
        self._medicamento_seleccionado = None

        self.tabla_medicamentos.cellClicked.connect(self._on_medicamento_seleccionado)
        self.search_bar.textChanged.connect(self._filtrar_medicamentos)

        self.btn_prescribir.clicked.connect(self._guardar)
        self.btn_cancelar.clicked.connect(self.reject)

    def cargar_medicamentos(self, lista):
        self._medicamentos = lista
        self._mostrar_medicamentos(lista)

    def _mostrar_medicamentos(self, lista):
        self.tabla_medicamentos.setRowCount(0)
        for med in lista:
            row = self.tabla_medicamentos.rowCount()
            self.tabla_medicamentos.insertRow(row)
            item_nombre = self._item(med.nombre)
            item_nombre.setData(Qt.UserRole, med)
            self.tabla_medicamentos.setItem(row, 0, item_nombre)
            self.tabla_medicamentos.setItem(row, 1, self._item(med.categoria))
        self.tabla_medicamentos.resizeColumnsToContents()

    def _filtrar_medicamentos(self, texto):
        filtrados = [m for m in self._medicamentos if texto.lower() in m.nombre.lower() or texto.lower() in m.categoria.lower()]
        self._mostrar_medicamentos(filtrados)

    def _on_medicamento_seleccionado(self, fila):
        med = self.tabla_medicamentos.item(fila, 0)
        if med is None:
            return
        self._medicamento_seleccionado = med.data(Qt.UserRole)
        if self._medicamento_seleccionado:
            self.lbl_med_seleccionado.setText(self._medicamento_seleccionado.nombre)
            self.btn_prescribir.setEnabled(True)

    def _item(self, texto):
        from PyQt5.QtWidgets import QTableWidgetItem
        return QTableWidgetItem(str(texto))

    def _guardar(self):
        # Validación de contenidos vacíos
        if not self.edit_dosis.text():
            QMessageBox.warning(self, "Campos vacíos", "Rellena el campo de dosis.")
            return
        
        if not self.edit_frecuencia.text():
            QMessageBox.warning(self, "Campos vacíos", "Rellena el campo de frecuencia.")
            return
        
        if self._medicamento_seleccionado is None:
            QMessageBox.warning(self, "Medicamento no seleccionado", "Por favor, selecciona un medicamento de la lista.")
            return
        
        try:
            dosis = int(self.edit_dosis.text())
            if self.controlador:
                self.controlador.guardar_receta(
                    id_medicamento=self._medicamento_seleccionado.id_medicamento,
                    dosis=dosis,
                    frecuencia=self.edit_frecuencia.text(),
                    via=self.combo_via.currentText(),
                    fecha_inicio=self.date_inicio.date().toString('yyyy-MM-dd'),
                    fecha_fin=self.date_fin.date().toString('yyyy-MM-dd'),
                    notas=self.edit_notas.toPlainText(),
                    id_paciente=self._paciente.id_paciente,
                    id_ingreso=self._paciente.id_ingreso
                )
            self.accept()

        except ValueError:
            QMessageBox.warning(self, "Error de tipo", "La dosis debe ser un número entero.")