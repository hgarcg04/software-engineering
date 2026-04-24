import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QButtonGroup, QMessageBox, QTableWidgetItem
)
from PyQt5.QtCore import QTimer, QDateTime, Qt
from PyQt5 import uic

ui_path = os.path.join(os.path.dirname(__file__), "Ui/VistaEnfermero.ui")
Form, Window = uic.loadUiType(ui_path)

class VentanaEnfermeros(QMainWindow, Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.btn_logout.clicked.connect(self.cerrar_sesion)
        self.tabla_pacientes.cellClicked.connect(self._on_paciente_clicked)
        self.btn_deseleccionar.clicked.connect(self.deseleccionar_paciente)
        self.search_bar.textChanged.connect(self._filtrar_pacientes)

        self._todos_los_pacientes = [] 
        self._paciente_activo = None
        self.btn_nuevo_registro.setEnabled(False)
        self.btn_suministrar.setEnabled(False)
        self._actualizar_banner_inicio()


        self.timer = QTimer(self)
        self.timer.timeout.connect(self.actualizar_fecha_hora)
        self.timer.start(1000)
        self.actualizar_fecha_hora()

    def cargar_datos_iniciales(self, lista):
        self._todos_los_pacientes = lista 
        self.mostrar_tabla_pacientes(lista)



    # -----------------------------------------------------------------------
    # RELOJ
    # -----------------------------------------------------------------------

    def actualizar_fecha_hora(self):
        fecha_actual = QDateTime.currentDateTime()
        self.lbl_datetime.setText(fecha_actual.toString("dd/MM/yyyy  HH:mm"))


    # -----------------------------------------------------------------------
    # CERRAR SESIÓN
    # -----------------------------------------------------------------------
    def cerrar_sesion(self):
        print("Cerrando sesión...")
        self.close()

    # -----------------------------------------------------------------------
    # TABLA INICIAL DE PACIENTES INGRESADO
    # -----------------------------------------------------------------------
  
    def mostrar_tabla_pacientes(self, lista):
        self.tabla_pacientes.setRowCount(len(lista))
        
        for fila, pac in enumerate(lista):
            datos = [pac.nif, pac.nombre, pac.apellido1, pac.apellido2, 
                    str(pac.fecha_nacimiento), pac.genero, 
                    str(pac.fecha_registro), pac.medico_asignado]
            
            for col, valor in enumerate(datos):
                item = QTableWidgetItem(str(valor))
                item.setTextAlignment(Qt.AlignCenter)
                item.setData(Qt.UserRole, pac) 
                self.tabla_pacientes.setItem(fila, col, item)
        
    # -------------------------------------------------------------------------
    # BÚSQUEDA DINÁMICA
    # -------------------------------------------------------------------------

    def _filtrar_pacientes(self, texto):
        texto = texto.strip().lower()
        
        # Si el usuario borra todo el texto, mostramos la lista original completa
        if not texto:
            filtrados = self._todos_los_pacientes
        else:
            # Filtramos basándonos en los atributos del objeto VO
            filtrados = [
                p for p in self._todos_los_pacientes
                if texto in p.nombre.lower() or 
                   texto in p.apellido1.lower() or 
                   texto in p.apellido2.lower()
            ]
            
        self.mostrar_tabla_pacientes(filtrados)
    # -----------------------------------------------------------------------
    # SELECCIÓN / DESELECCIÓN DE PACIENTE
    # -----------------------------------------------------------------------
    def _on_paciente_clicked(self, fila):
        item = self.tabla_pacientes.item(fila, 0)
        if item is None:
            return

        self._paciente_activo = item.data(Qt.UserRole)
        self._actualizar_banner_inicio()
        self.btn_nuevo_registro.setEnabled(True)
        self.btn_suministrar.setEnabled(True)

    def deseleccionar_paciente(self):
        self._paciente_activo = None
        self.tabla_pacientes.clearSelection()
        self.btn_nuevo_registro.setEnabled(False)
        self.btn_suministrar.setEnabled(False)

        self._actualizar_banner_inicio()

    def _actualizar_banner_inicio(self):
        if self._paciente_activo:
            nombre_completo = f"{self._paciente_activo.nombre} {self._paciente_activo.apellido1}"
            self.lbl_paciente_sel_nombre.setText(nombre_completo)

        else:
            self.lbl_paciente_sel_nombre.setText("Ninguno")
            
    # -----------------------------------------------------------------------
    # CONTROLADOR (property)
    # -----------------------------------------------------------------------
    @property
    def controlador(self):
        return self._controlador

    @controlador.setter
    def controlador(self, ref_controlador):
        self._controlador = ref_controlador


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaEnfermeros()
    ventana.show()
    sys.exit(app.exec_())
