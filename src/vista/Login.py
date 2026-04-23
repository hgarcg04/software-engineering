import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))  


from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import uic
from src.modelo.VO.LoginVO import LoginVO

ui_path = os.path.join(os.path.dirname(__file__), "Ui/VistaLogin.ui")
Form, Window = uic.loadUiType(ui_path)


class MiVentana(QMainWindow, Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)  
        self.controlador = None

        self.btn_login.clicked.connect(self.on_button_click)

    def on_button_click(self):
        texto_nombre = self.edit_user.text()  
        texto_password = self.edit_pass.text() 

        loginVO = LoginVO(texto_nombre, texto_password)
        if self._controlador:
            self._controlador.comprobarLogin(loginVO)
        
    def cerrar(self):      
        self.close()

      
    @property
    def controlador(self):
        return self._controlador
    
    @controlador.setter
    def controlador(self, ref_controlador):
        self._controlador = ref_controlador

