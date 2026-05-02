import os
from PyQt5.QtWidgets import QDialog
from PyQt5 import uic

ui_path = os.path.join(os.path.dirname(__file__), "Ui/DialogoEpisodio.ui")
Form, _ = uic.loadUiType(ui_path)


class DialogoEpisodio(QDialog, Form):

    NUEVO_EPISODIO = "nuevo"
    EPISODIO_EXISTENTE = "existente"

    def __init__(self, parent=None, paciente_nombre='', episodios=None):
        super().__init__(parent)
        self.setupUi(self)

        self._episodios = episodios or []
        self.resultado = None       # NUEVO_EPISODIO o EPISODIO_EXISTENTE
        self.episodio_seleccionado = None  # EpisodioVO seleccionado o None

        self.lbl_pac_nombre.setText(paciente_nombre)

        self._cargar_episodios()

        self.tabla_episodios.itemSelectionChanged.connect(self._on_seleccion)
        self.btn_usar_episodio.clicked.connect(self._usar_existente)
        self.btn_nuevo_episodio.clicked.connect(self._nuevo_episodio)
        self.btn_cancelar.clicked.connect(self.reject)

    def _cargar_episodios(self):
        self.tabla_episodios.setRowCount(0)
        for ep in self._episodios:
            row = self.tabla_episodios.rowCount()
            self.tabla_episodios.insertRow(row)
            self.tabla_episodios.setItem(row, 0, self._item(str(ep.fecha_hora_inicio)[:16]))
            self.tabla_episodios.setItem(row, 1, self._item(ep.tipo if ep.tipo else ''))
            self.tabla_episodios.setItem(row, 2, self._item(ep.diagnostico if ep.diagnostico else ''))
        self.tabla_episodios.resizeColumnsToContents()

    def _on_seleccion(self):
        fila = self.tabla_episodios.currentRow()
        self.btn_usar_episodio.setEnabled(fila >= 0)

    def _usar_existente(self):
        fila = self.tabla_episodios.currentRow()
        if fila < 0:
            return
        self.resultado = self.EPISODIO_EXISTENTE
        self.episodio_seleccionado = self._episodios[fila]
        self.accept()

    def _nuevo_episodio(self):
        self.resultado = self.NUEVO_EPISODIO
        self.episodio_seleccionado = None
        self.accept()

    def _item(self, texto):
        from PyQt5.QtWidgets import QTableWidgetItem
        return QTableWidgetItem(str(texto))
