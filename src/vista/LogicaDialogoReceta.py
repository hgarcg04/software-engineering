import os
from PyQt5.QtWidgets import QDialog
from PyQt5 import uic
from PyQt5.QtWidgets import QMessageBox

ui_path = os.path.join(os.path.dirname(__file__), "Ui/DialogoReceta.ui")
Form, _ = uic.loadUiType(ui_path)

class DialogoReceta(QDialog, Form):
    def __init__(self, parent=None, paciente_vo=None):
        super().__init__(parent)
        self.setupUi(self)
        self._paciente = paciente_vo
        self.controlador = None
        self._id_medicamento_seleccionado = None
        self._id_paciente = None
        self.lbl_pac_nombre.setText('— Sin paciente —')
        self._id_medicamento_seleccionado = None
        self._id_paciente = None
        self._medicamentos = []

        self.tabla_medicamentos.itemSelectionChanged.connect(self._on_medicamento_seleccionado)
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
            self.tabla_medicamentos.setItem(row, 0, self._item(med.nombre))
            self.tabla_medicamentos.setItem(row, 1, self._item(med.categoria))
        self.tabla_medicamentos.resizeColumnsToContents()

    def _filtrar_medicamentos(self, texto):
        filtrados = [m for m in self._medicamentos if texto.lower() in m.nombre.lower() or texto.lower() in m.categoria.lower()]
        self._mostrar_medicamentos(filtrados)

    def _on_medicamento_seleccionado(self):
        fila = self.tabla_medicamentos.currentRow()
        if fila < 0:
            return
        med = self._medicamentos[fila]
        self._id_medicamento_seleccionado = med.id_medicamento
        self.lbl_med_seleccionado.setText(med.nombre)
        self.btn_prescribir.setEnabled(True)

    def _item(self, texto):
        from PyQt5.QtWidgets import QTableWidgetItem
        return QTableWidgetItem(str(texto))

    def _guardar(self):
        # Validación básica
        if not self.edit_dosis.text() or not self.edit_frecuencia.text():
            QMessageBox.warning(self, "Campos vacíos", "Rellena al menos la dosis y la frecuencia.")
            return
        
        if self.controlador:
            self.controlador.guardar_receta(
                id_medicamento=self._id_medicamento_seleccionado,
                dosis=self.edit_dosis.text(),
                frecuencia=self.edit_frecuencia.text(),
                via=self.combo_via.currentText(),
                fecha_inicio=self.date_inicio.date().toString('yyyy-MM-dd'),
                fecha_fin=self.date_fin.date().toString('yyyy-MM-dd'),
                notas=self.edit_notas.toPlainText(),
                id_paciente=self._id_paciente
            )
        self.accept()