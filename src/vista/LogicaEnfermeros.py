import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from PyQt5.QtWidgets import QApplication, QMainWindow, QButtonGroup, QMessageBox, QTableWidgetItem
from PyQt5.QtCore import QTimer, QDateTime

from PyQt5 import uic

ui_path = os.path.join(os.path.dirname(__file__), "Ui/VistaEnfermero.ui")
Form, Window = uic.loadUiType(ui_path)

class MiVentana(QMainWindow, Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.cargar_datos_iniciales()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.actualizar_fecha_hora)
        self.timer.start(1000)  # Actualiza cada 1000 milisegundos (1 segundo)
        
        # Llamada inicial para no esperar 1 segundo a que aparezca al abrir
        self.actualizar_fecha_hora()
        
        # --- LÓGICA DE NAVEGACIÓN ---
        # Agrupamos los botones para que solo uno esté "checked" a la vez
        self.nav_group = QButtonGroup()
        self.nav_group.addButton(self.btn_nav_inicio)
        self.nav_group.addButton(self.btn_nav_constantes)
        self.nav_group.addButton(self.btn_nav_medicacion)
        self.nav_group.addButton(self.btn_nav_episodios)
        self.nav_group.setExclusive(True)

        # Conectamos la navegación
        self.btn_nav_inicio.clicked.connect(lambda: self.stackedPanel.setCurrentIndex(0))
        self.btn_nav_constantes.clicked.connect(lambda: self.stackedPanel.setCurrentIndex(1))
        self.btn_nav_medicacion.clicked.connect(lambda: self.stackedPanel.setCurrentIndex(2))
        self.btn_nav_episodios.clicked.connect(lambda: self.stackedPanel.setCurrentIndex(3))

        # --- CONEXIÓN DE BOTONES ---
        self.btn_logout.clicked.connect(self.cerrar_sesion)
        self.btn_guardar_constante.clicked.connect(self.guardar_constante)
        self.btn_confirmar_medicacion.clicked.connect(self.confirmar_medicacion)

        # --- INICIALIZACIÓN ---
        self.controlador = None
    

    def actualizar_fecha_hora(self):
        # Obtiene la fecha y hora actual del sistema
        fecha_actual = QDateTime.currentDateTime()
        
        # Define el formato (ejemplo: 23/04/2026 15:58)
        formato = "dd/MM/yyyy  HH:mm"
        
        # Actualiza el texto del label que definiste en el UI
        self.lbl_datetime.setText(fecha_actual.toString(formato))

    def cargar_datos_iniciales(self):
        # Datos de prueba
        datos = [(1, 'Yonathan', '71997812K', 3, 'Dr. Gonzalez'), 
                 (34, 'Maria', '717198L', 2, 'Dra. Garcia')]
        self.actualizar_tabla_pacientes(datos)


    def cerrar_sesion(self):
        print("Cerrando sesión...")
        self.close()

    def guardar_constante(self):
        # Captura de datos del formulario de constantes
        constante = self.combo_constante.currentText()
        valor = self.edit_valor_constante.text()
        observaciones = self.edit_observaciones.toPlainText()
        
        print(f"--- Guardando Constante ---")
        print(f"Tipo: {constante}, Valor: {valor}, Obs: {observaciones}")
        # Aquí llamarías al controlador más adelante

    def confirmar_medicacion(self):
        # Captura de datos del formulario de medicación
        categoria = self.combo_categoria.currentText()
        cantidad = self.spin_cantidad.value()
        notas = self.edit_notas_med.toPlainText()
        
        print(f"--- Suministrando Medicación ---")
        print(f"Categoría: {categoria}, Cantidad: {cantidad}, Notas: {notas}")
        # Aquí llamarías al controlador más adelante
    


    def actualizar_tabla_pacientes(self, lista_pacientes):
        """
        lista_pacientes: debe ser una lista de objetos o tuplas 
        ej: [(id, nombre, dni, hab, medico), (...)]
        """
        lista_pacientes = [(1, 'Yonathan', '71997812K', 3, 'Dr. Gonzalez' ), (34, 'Maria', '717198L', 2, 'Dra. Garcia')]
        # 1. Ajustar el número de filas al tamaño de los datos
        self.tabla_pacientes.setRowCount(len(lista_pacientes))

        # 2. Rellenar la tabla
        for fila_index, paciente in enumerate(lista_pacientes):
            # Asumiendo que 'paciente' es una lista/tupla con los 5 campos definidos en tu UI
            self.tabla_pacientes.setItem(fila_index, 0, QTableWidgetItem(str(paciente[0]))) # ID
            self.tabla_pacientes.setItem(fila_index, 1, QTableWidgetItem(str(paciente[1]))) # Nombre
            self.tabla_pacientes.setItem(fila_index, 2, QTableWidgetItem(str(paciente[2]))) # DNI
            self.tabla_pacientes.setItem(fila_index, 3, QTableWidgetItem(str(paciente[3]))) # Habitación
            self.tabla_pacientes.setItem(fila_index, 4, QTableWidgetItem(str(paciente[4]))) # Médico

    @property
    def controlador(self):
        return self._controlador
    
    @controlador.setter
    def controlador(self, ref_controlador):
        self._controlador = ref_controlador

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = MiVentana()
    ventana.show()
    sys.exit(app.exec_())