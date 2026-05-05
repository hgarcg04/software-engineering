from PyQt5.QtWidgets import QApplication, QMainWindow
from src.vista.LogicaLogin import MiVentana
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


    # 3. Si un enfermero añade varias tomas de la temperatura a la lista de pendientes, y luego las guarda todas a la vez,
    # con el botonde "guardar todo" se reistran todas las tomas exactemnte a la misma hora -> problema con la gráfica.
