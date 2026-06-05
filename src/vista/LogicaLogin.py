import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))  


from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5 import uic
from PyQt5.QtCore import QTimer

ui_path = os.path.join(os.path.dirname(__file__), "Ui/VistaLogin.ui")
Form, Window = uic.loadUiType(ui_path)




class MiVentana(QMainWindow, Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self._controlador = None

        self.btn_login.clicked.connect(self.on_button_click)
        self.btn_change_pass.clicked.connect(self.abrir_cambio_contrasena)
        self.btn_pw_confirmar.clicked.connect(self._cambiar_password)
        self.btn_pw_volver.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(0))

        self.edit_user.returnPressed.connect(lambda: self.edit_pass.setFocus())
        self.edit_pass.returnPressed.connect(self.on_button_click)

        self.input_pw_actual.returnPressed.connect(lambda: self.input_pw_nueva.setFocus())
        self.input_pw_nueva.returnPressed.connect(lambda: self.input_pw_confirmar.setFocus())
        self.input_pw_confirmar.returnPressed.connect(self._cambiar_password)


    def on_button_click(self):
        texto_nombre = self.edit_user.text()
        texto_password = self.edit_pass.text()
        if self._controlador:
            self._controlador.comprobarLogin(texto_nombre, texto_password)

    def abrir_cambio_contrasena(self):
        usuario = self.edit_user.text().strip()
        if not usuario:
            QMessageBox.warning(self, "Campo vacío", "Introduce tu nombre de usuario antes de cambiar la contraseña.")
            return
        self.input_pw_actual.clear()      # ← añadir este campo
        self.input_pw_nueva.clear()
        self.input_pw_confirmar.clear()
        self.lbl_pw_error_actual.setVisible(False)      # ← añadir
        self.lbl_pw_error_coincidencia.setVisible(False)
        self.lbl_pw_error_igual.setVisible(False)
        self.lbl_pw_ok.setVisible(False)
        self.stackedWidget.setCurrentIndex(1)
        self.input_pw_actual.setFocus()

    def _cambiar_password(self):
        usuario = self.edit_user.text().strip()
        actual = self.input_pw_actual.text().strip()
        nueva = self.input_pw_nueva.text().strip()
        confirmar = self.input_pw_confirmar.text().strip()

        self.lbl_pw_error_actual.setVisible(False)
        self.lbl_pw_error_coincidencia.setVisible(False)
        self.lbl_pw_error_igual.setVisible(False)
        self.lbl_pw_ok.setVisible(False)

        # 1. Verificar contraseña actual
        userVO = self._controlador.verificar_credenciales(usuario, actual)
        if userVO is None:
            self.lbl_pw_error_actual.setVisible(True)
            self.input_pw_actual.clear()
            return

        # 2. Verificar que nueva y confirmación coinciden
        if nueva != confirmar:
            self.lbl_pw_error_coincidencia.setVisible(True)
            self.input_pw_nueva.clear()
            self.input_pw_confirmar.clear()
            return

        # 3. Cambiar
        self._controlador.cambiar_password(nueva, userVO)
        self.lbl_pw_ok.setVisible(True)
        self.input_pw_actual.clear()
        self.input_pw_nueva.clear()
        self.input_pw_confirmar.clear()
        QMessageBox.information(self, "Éxito", "Contraseña actualizada correctamente.")
        self.stackedWidget.setCurrentIndex(0)
        self.limpiar_campos()


    def limpiar_campos(self):
        """ función que deja los campos de user y passw vacíos para cuando
            se cierre sesión y se vuelva a la ventana de login no aparezcan 
            los viejos """
        
        self.edit_user.clear()
        self.edit_pass.clear()
        self.edit_user.setFocus()

    def lanzar_warning(self):
        QMessageBox.warning(self, "Inicio de sesión incorrecto", f"Usuario y/o contraseña incorrectos.")

        
    def cerrar(self):   
        QTimer.singleShot(500, self.close)   
    

      
    @property
    def controlador(self):
        return self._controlador
    
    @controlador.setter
    def controlador(self, ref_controlador):
        self._controlador = ref_controlador

