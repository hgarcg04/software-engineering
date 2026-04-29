import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from PyQt5.QtWidgets import QMainWindow
from PyQt5 import uic
from PyQt5.QtCore import pyqtSignal

ui_path = os.path.join(os.path.dirname(__file__), "Ui/VistaAdministrativo.ui")

PAGE_INICIO = 0
PAGE_PACIENTES = 1
PAGE_CITAS = 2
PAGE_AGENDA = 3
PAGE_CREDENCIALES = 4
PAGE_MEDICAMENTOS = 5
PAGE_BACKUP = 6

Form, Window = uic.loadUiType(ui_path)

class VentanaAdministrativos(QMainWindow, Form):
    signal_logout = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.controlador = None

        # Navegación entre páginas
        self.btn_nav_inicio.clicked.connect(lambda: self._navegar(PAGE_INICIO))
        self.btn_nav_pacientes.clicked.connect(lambda: self._navegar(PAGE_PACIENTES))
        self.btn_nav_citas.clicked.connect(lambda: self._navegar(PAGE_CITAS))
        self.btn_nav_agenda.clicked.connect(lambda: self._navegar(PAGE_AGENDA))
        self.btn_nav_credenciales.clicked.connect(lambda: self._navegar(PAGE_CREDENCIALES))
        self.btn_nav_medicamentos.clicked.connect(lambda: self._navegar(PAGE_MEDICAMENTOS))
        self.btn_nav_backup.clicked.connect(lambda: self._navegar(PAGE_BACKUP))

        self.btn_logout.clicked.connect(self.cerrar_sesion)

    def cerrar_sesion(self):
        print("Cerrando sesión...")
        self.signal_logout.emit()
        self.close()

    def _navegar(self, indice):
        """
            Método para abrir la pestaña que se le pasa como argumento
        """
        self.stackedWidget.setCurrentIndex(indice)
        nav_btns = [
            self.btn_nav_inicio,
            self.btn_nav_pacientes,
            self.btn_nav_citas,
            self.btn_nav_agenda,
            self.btn_nav_credenciales,
            self.btn_nav_medicamentos,
            self.btn_nav_backup
        ]
        for i, btn in enumerate(nav_btns):
            btn.setChecked(i == indice)

    @property
    def controlador(self):
        return self._controlador

    @controlador.setter
    def controlador(self, ref):
        self._controlador = ref