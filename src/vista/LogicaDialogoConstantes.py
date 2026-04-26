import sys
import os


from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QButtonGroup, QMessageBox, QTableWidgetItem, QDialog
from PyQt5.QtCore import QTimer, QDateTime, Qt, pyqtSignal
from PyQt5.QtWidgets import QHeaderView

from src.modelo.VO.UsuariosVO import UserVO
from src.modelo.VO.ConstantesVO import ConstantesVO


sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
ui_path = os.path.join(os.path.dirname(__file__), "Ui/DialogoHistoricoConstantes.ui")


Form, Window = uic.loadUiType(ui_path)

class DialogoHistorico(QDialog, Form):
    def __init__(self, paciente, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self._paciente = paciente
        self._controlador = None

        ahora = QDateTime.currentDateTime()
        self.date_desde.setDateTime(ahora.addDays(-7))  
        self.date_hasta.setDateTime(ahora)   

        self.lbl_paciente.setText(f"Paciente: {paciente.nombre_completo} | IngresoID: {paciente.id_ingreso} | Episodio: {paciente.id_episodio}")
        self.btn_consultar.clicked.connect(self._consultar)
        self.btn_generar_grafico.clicked.connect(self._generar_grafico)
        self.btn_generar_grafico.setEnabled(False)


    def _consultar(self):

        # DUDA: ¿Crear un VO para esta tupla?
        tipo  = self.combo_constante.currentText()
        desde = self.date_desde.dateTime().toString("yyyy-MM-dd HH:mm")
        hasta = self.date_hasta.dateTime().toString("yyyy-MM-dd HH:mm")
        print("tipo:", tipo)
        print("Desde: ",desde)
        print("Hasta:", hasta)
        print("Id episodio:", self._paciente.id_episodio)
        if self._controlador:
            self._controlador.consultar_historico(
                self._paciente.id_episodio, tipo, desde, hasta
            )
        

    def cargar_resultados(self, lista):
        print("Intentando mostrar las constantes")
        self.tabla_historico.setRowCount(len(lista))
        for fila, c in enumerate(lista):

            item0 = QTableWidgetItem(str(c.fecha))
            item0.setTextAlignment(Qt.AlignCenter)
            self.tabla_historico.setItem(fila, 0, item0)

            item1 = QTableWidgetItem(str(c.hora)[:5])
            item1.setTextAlignment(Qt.AlignCenter)
            self.tabla_historico.setItem(fila, 1, item1)

            item2 = QTableWidgetItem(str(c.valor))
            item2.setTextAlignment(Qt.AlignCenter)
            self.tabla_historico.setItem(fila, 2, item2)

            self.tabla_historico.setItem(fila, 3, QTableWidgetItem(str(c.observaciones) if c.observaciones else "—"))

        self.btn_generar_grafico.setEnabled(len(lista) > 0)
    
    def _generar_grafico(self):
        pass
    @property
    def controlador(self):
        return self._controlador

    @controlador.setter
    def controlador(self, ref):
        self._controlador = ref