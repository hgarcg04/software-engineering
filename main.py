from PyQt5.QtWidgets import QApplication, QMainWindow
from src.vista.Login import MiVentana
from src.modelo.Logica import Logica
from src.controlador.ControladorPrincipal import ControladorPrincipal


if __name__ == "__main__":
    app = QApplication([])
    ventana = MiVentana()
    modelo = Logica()
    controlador = ControladorPrincipal(ventana, modelo)

    ventana.controlador = controlador
    controlador.ventanaInciarSesion()

    app.exec_()

    
    
