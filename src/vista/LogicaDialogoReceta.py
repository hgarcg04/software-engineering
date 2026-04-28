import os
from PyQt5.QtWidgets import QDialog
from PyQt5 import uic

ui_path = os.path.join(os.path.dirname(__file__), "Ui/DialogoReceta.ui")
Form, _ = uic.loadUiType(ui_path)

class DialogoReceta(QDialog, Form):
    def __init__(self, parent=None, paciente_vo=None):
        super().__init__(parent)
        self.setupUi(self)
        self._paciente = paciente_vo
        self.controlador = None

        self.btn_guardar_receta.clicked.connect(self._guardar)
        self.btn_cancelar.clicked.connect(self.reject)

    #def _guardar(self):
    #    if self.controlador:
    #        self.controlador.guardar_receta(...)
    #    self.accept()