from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import uic
from src.modelo.BusinessObject import BusssinesObject
from src.modelo.VO.LoginVO import LoginVO
import os.path
os.path.dirname(os.path.abspath(__file__))

# Cargar la interfaz generada desde el archivo .ui
Form, Window = uic.loadUiType("./src/vista/Ui/VistaLogin.ui")


class MiVentana(QMainWindow, Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)  # Inicializa los widgets
        self.controlador = None

        # Conectar el botón a la función
        self.btn_login.clicked.connect(self.on_button_click)

    def on_button_click(self):
        print("Botón presionado")
        texto_nombre = self.edit_user.text()  # Obtener el texto del campo nombre
        texto_password = self.edit_pass.text() # obtener el texto del campo contraseña

        login = LoginVO(texto_nombre, texto_password)


        print("El texto es: ")
        print(texto_nombre)
    

        
    @property
    def controlador(self):
        return self._controlador
    
    @controlador.setter
    def controlador(self, ref_controlador):
        self._controlador = ref_controlador



if __name__ == "__main__":
    app = QApplication([])
    ventana = MiVentana()
    ventana.show()
    app.exec_()
