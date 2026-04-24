from src.vista.LogicaEnfermeros import VentanaEnfermeros
from src.modelo.VO.PacientesVO import PacientesVO

class ControladorEnfermeros:
    def __init__(self, vista, dao):
        self._vista = vista
        self._modelo = dao

        self._cargar_pacientes()

    def _cargar_pacientes(self):
        lista_pacientes = self._modelo.obtenerPacientes()
        if lista_pacientes:
            self._vista.cargar_datos_iniciales(lista_pacientes)