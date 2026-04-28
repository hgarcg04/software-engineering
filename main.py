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

    
    # COSAS A ARREGLAR:
    # 1. Al cerrar el dialogo de constantes vitales tengo que volver a poner la referencia de la vista a la
    # ventana de enfermeros.

    # 2. Si no hay paciente seleccionado, al viajar por las pestañas desde la barra lateral, 
    # no debería aparecer ningun dato (en vez de actualizar al presionar el boton de ej: "suministro" de la barra lateral,
    # actualizar on cell clicked)
