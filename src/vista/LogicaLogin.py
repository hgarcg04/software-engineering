import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))  


from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import uic
from PyQt5.QtCore import QTimer

ui_path = os.path.join(os.path.dirname(__file__), "Ui/VistaLogin.ui")
Form, Window = uic.loadUiType(ui_path)




class MiVentana(QMainWindow, Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)  
        self.controlador = None

        self.btn_login.clicked.connect(self.on_button_click)
        self.edit_user.returnPressed.connect(lambda: self.edit_pass.setFocus())
        self.edit_pass.returnPressed.connect(self.on_button_click)

    def on_button_click(self):
        texto_nombre = self.edit_user.text()  
        texto_password = self.edit_pass.text() 

        if self._controlador:
            self._controlador.comprobarLogin(texto_nombre, texto_password)
        
        


    def limpiar_campos(self):
        """ función que deja los campos de user y passw vacíos para cuando
            se cierre sesión y se vuelva a la ventana de login no aparezcan 
            los viejos """
        
        self.edit_user.clear()
        self.edit_pass.clear()
        self.edit_user.setFocus()

        
    def cerrar(self):   
        QTimer.singleShot(500, self.close)   
    

      
    @property
    def controlador(self):
        return self._controlador
    
    @controlador.setter
    def controlador(self, ref_controlador):
        self._controlador = ref_controlador

