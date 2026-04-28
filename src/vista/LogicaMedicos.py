import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from PyQt5.QtWidgets import QMainWindow
from PyQt5 import uic
from PyQt5.QtCore import pyqtSignal
from src.vista.LogicaDialogoReceta import DialogoReceta

ui_path = os.path.join(os.path.dirname(__file__), "Ui/VistaMedico.ui")
Form, Window = uic.loadUiType(ui_path)

class VentanaMedico(QMainWindow, Form):
    signal_logout = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.controlador = None

        # Navegación entre páginas
        self.btn_nav_inicio.clicked.connect(lambda: self.stackedPanel.setCurrentIndex(0))
        self.btn_nav_agenda.clicked.connect(lambda: self.stackedPanel.setCurrentIndex(1))
        self.btn_nav_consulta.clicked.connect(lambda: self.stackedPanel.setCurrentIndex(2))
        self.btn_nav_receta.clicked.connect(lambda: self.stackedPanel.setCurrentIndex(3))
        self.btn_nav_hcd.clicked.connect(lambda: self.stackedPanel.setCurrentIndex(4))

        self.btn_logout.clicked.connect(self.cerrar_sesion)

    def cerrar_sesion(self):
        print("Cerrando sesión...")
        self.signal_logout.emit()
        self.close()

    def abrir_dialogo_receta(self):
        dialogo = DialogoReceta(parent=self, paciente_vo=self._paciente_activo)
        dialogo.exec_()

    @property
    def controlador(self):
        return self._controlador

    @controlador.setter
    def controlador(self, ref):
        self._controlador = ref