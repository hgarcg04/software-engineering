import sys
import os


from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QButtonGroup, QMessageBox, QTableWidgetItem
from PyQt5.QtCore import QTimer, QDateTime, Qt, pyqtSignal
from PyQt5.QtWidgets import QHeaderView

from src.modelo.VO.UsuariosVO import UserVO
from src.modelo.VO.ConstantesVO import ConstantesVO
from src.vista.LogicaDialogoConstantes import DialogoHistorico


sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
ui_path = os.path.join(os.path.dirname(__file__), "Ui/VistaEnfermero.ui")



PAGE_INICIO     = 0
PAGE_CONSTANTES = 1
PAGE_MEDICACION = 2
PAGE_EPISODIOS  = 3
PAGE_DETALLES   = 4

Form, Window = uic.loadUiType(ui_path)

class VentanaEnfermeros(QMainWindow, Form):
    signal_logout = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setupUi(self)
     


        # Encabezado de la tabla de pacientes 
        header = self.tabla_pacientes.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        

        # -----------------------------------------------------------------------------
        # BOTONES
        # -----------------------------------------------------------------------------

        # --- Navegación ---

        self.btn_nav_inicio.clicked.connect(lambda: self._navegar(PAGE_INICIO))
        self.btn_nav_constantes.clicked.connect(lambda: self._navegar(PAGE_CONSTANTES))
        self.btn_nav_constantes.clicked.connect(lambda: self.edit_valor_constante.setFocus())
     
        self.btn_nav_medicacion.clicked.connect(lambda: self._navegar(PAGE_MEDICACION))
        self.btn_nav_episodios.clicked.connect(lambda: self._navegar(PAGE_EPISODIOS))
        self.btn_ver_registros.clicked.connect(self._abrir_detalles_ingreso)
        self.btn_cerrar_detalles_ingreso.clicked.connect(lambda: self._navegar(PAGE_DETALLES))
        self.btn_suministrar.clicked.connect(lambda: self._navegar(PAGE_MEDICACION))
        self.btn_nuevo_registro.clicked.connect(lambda: self._navegar(PAGE_CONSTANTES))
        self.btn_nuevo_registro.clicked.connect(lambda: self.edit_valor_constante.setFocus())

        self.btn_nav_inicio.clicked.connect(lambda: self._navegar(PAGE_INICIO))
        self.btn_logout.clicked.connect(self.cerrar_sesion)

        # --- Gestion tabla pacientes ---
        self.tabla_pacientes.cellClicked.connect(self._on_paciente_clicked)
        self.btn_deseleccionar.clicked.connect(self.deseleccionar_paciente)
        self.search_bar.textChanged.connect(self._filtrar_pacientes)


        # --- Botones de pagina de constantes ---     
        self.btn_anadir_registro.clicked.connect(self.agregar_constante)
        self.btn_guardar_registro.clicked.connect(self.guardar_constantes)
        self.btn_borrar_todo.clicked.connect(self._borrar_todo)
        self.btn_borrar_seleccionado.clicked.connect(self._borrar_seleccionado)
        self.btn_ver_historico.clicked.connect(self.ver_historico)

        self.edit_valor_constante.returnPressed.connect(lambda: self.edit_observaciones.setFocus())
        self.combo_constante.activated.connect(lambda: self.edit_valor_constante.setFocus())
        self.btn_anadir_registro.clicked.connect(lambda: self.edit_valor_constante.setFocus())



        # -----------------------------------------------------------------------------
        # INICIALIZACIONES
        # -----------------------------------------------------------------------------

        self._todos_los_pacientes = [] 
        self._paciente_activo = None
        self._enfermero = None
        self._constantes_pendientes = []

        self.btn_nuevo_registro.setEnabled(False)
        self.btn_suministrar.setEnabled(False)
        self.btn_ver_registros.setEnabled(False)
        self._actualizar_banner_inicio()


        self.timer = QTimer(self)
        self.timer.timeout.connect(self.actualizar_fecha_hora)
        self.timer.start(1000)
        self.actualizar_fecha_hora()

        self._navegar(PAGE_INICIO)

    # -----------------------------------------------------------------------------
    # DATOS INICIALES
    # -----------------------------------------------------------------------------

    def cargar_datos_iniciales(self, lista, userVO):
        """
            Método que recibe una lista de pacientes y la muestra en la interfaz.
            Además, recibe del controlador, el VO del usuario (enferemo). Tomamos el nombre y 
            lo ponemos en la cabecera de la ventana.
        """
        self._todos_los_pacientes = lista 
        self.mostrar_tabla_pacientes(lista)
        self._enfermero = userVO
        self.lbl_user_name.setText(f"Enfermero/a: {self._enfermero.nombre} {self._enfermero.apellidos}")




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
        """
            Método que manda un señal al controlador principal
            para que vuelva al login tras cerrar la ventana actual.
        """

        print("Cerrando sesión...")
        self.signal_logout.emit()
        self.close()

    # -----------------------------------------------------------------------
    # NAGEACIÓN
    # -----------------------------------------------------------------------

    def _navegar(self, indice):
        """
            Método para abrir la pestaña que se le pasa como argumento
        """
        self.stackedPanel.setCurrentIndex(indice)
        nav_btns = [
            self.btn_nav_inicio,
            self.btn_nav_constantes,
            self.btn_nav_medicacion,
            self.btn_nav_episodios,
        ]
        for i, btn in enumerate(nav_btns):
            btn.setChecked(i == indice)
    
    def _abrir_detalles_ingreso(self):
        if self._paciente_activo is None:
            return None
        else:
            self._poblar_detalles(self._paciente_activo)
            self._navegar(PAGE_DETALLES)
    
    def _poblar_detalles(self, pac):
        self.lbl_det_nif.setText(str(pac.nif))
        self.lbl_det_nombre.setText(f"{pac.nombre} {pac.apellido1} {pac.apellido2}")
        self.lbl_det_fnac.setText(str(pac.fecha_nacimiento))
        self.lbl_det_genero.setText(str(pac.genero))
        self.lbl_det_habitacion.setText(str(pac.num_habitacion))
        self.lbl_det_fingreso.setText(str(pac.fecha_ingreso)[:16] if pac.fecha_ingreso else "—")
        self.lbl_det_medico.setText(str(pac.medico_asignado))
        self.lbl_det_dieta.setText(str(pac.dieta) if pac.dieta else "—")
    



    # ---------------------------------------------------------------------------------------------------------------------------------------------------
    #                                                                   PÁGINA DE INICIO
    # ---------------------------------------------------------------------------------------------------------------------------------------------------
  
    def mostrar_tabla_pacientes(self, lista):
        self.tabla_pacientes.setRowCount(len(lista))
        
        for fila, pac in enumerate(lista):
            fecha_inicio_epi = str(pac.fecha_ingreso)[:16] if pac.fecha_ingreso else "—"

            datos = [
                pac.nif,
                pac.nombre_completo,
                pac.num_habitacion,
                pac.medico_asignado,
                str(fecha_inicio_epi)
            ]
            
            for col, valor in enumerate(datos):
                item = QTableWidgetItem(str(valor))
                item.setTextAlignment(Qt.AlignCenter)
                item.setData(Qt.UserRole, pac)  
                self.tabla_pacientes.setItem(fila, col, item)    

    # -------------------------------------------------------------------------
    # BÚSQUEDA DINÁMICA EN TABLA DE INICIO
    # -------------------------------------------------------------------------

    def _filtrar_pacientes(self, texto):
        texto = texto.strip().lower()
        
        if not texto:
            filtrados = self._todos_los_pacientes
        else:
            filtrados = [
                p for p in self._todos_los_pacientes
                if texto in p.nif.lower() or
                texto in p.nombre.lower() or 
                texto in p.apellido1.lower() or 
                texto in p.apellido2.lower() or
                texto in f"{p.nombre} {p.apellido1}".lower() or     
                texto in f"{p.apellido1} {p.apellido2}".lower() or   
                texto in f"{p.nombre} {p.apellido1} {p.apellido2}".lower()  
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
        self.btn_ver_registros.setEnabled(True)


    def deseleccionar_paciente(self):
        self._paciente_activo = None
        self.tabla_pacientes.clearSelection()
        self.btn_nuevo_registro.setEnabled(False)
        self.btn_suministrar.setEnabled(False)
        self.btn_ver_registros.setEnabled(False)

        self._actualizar_banner_inicio()

    def _actualizar_banner_inicio(self):
        if self._paciente_activo:
            nombre_completo = f"{self._paciente_activo.nombre} {self._paciente_activo.apellido1}"
            self.lbl_paciente_sel_nombre.setText(nombre_completo)
            self.lbl_paciente_sel_nombre_2.setText(nombre_completo)
            self.lbl_paciente_sel_nombre3.setText(nombre_completo)


        else:
            self.lbl_paciente_sel_nombre.setText("Ninguno")
            self.lbl_paciente_sel_nombre_2.setStyleSheet("color: #00b894; font-weight: bold;")
            self.lbl_paciente_sel_nombre_2.setText("— Sin paciente seleccionado —")
            self.lbl_paciente_sel_nombre3.setStyleSheet("color: #00b894; font-weight: bold;")
            self.lbl_paciente_sel_nombre3.setText("— Sin paciente seleccionado —")

    
    # ----------------------------------------------------------------------------------------------------------------------------------------------------------
    #                                                      PÁGINA DE REGISTRO DE CONSTANTES VITALES
    # ----------------------------------------------------------------------------------------------------------------------------------------------------------


    def agregar_constante(self):

        """
            Método que añade un nuevo registro de una constante concreta.
        """
        if self._paciente_activo is None:
            QMessageBox.warning(self, "Sin paciente", "No hay paciente activo. Vuelve al inicio y selecciona uno.")
            return
        constante     = self.combo_constante.currentText()
        valor         = self.edit_valor_constante.text()
        observaciones = self.edit_observaciones.toPlainText()


        if not valor:
            QMessageBox.warning(self, "Campo vacío", "Introduce un valor para la constante.")
            return
        
        # Se agrega el registro a la lista de registros listos para ser guardados
        self._constantes_pendientes.append({"tipo" : constante, 
                                            "valor": valor,
                                            "observaciones": observaciones})


        self._actualizar_tabla_pendientes()
        self.edit_valor_constante.clear()
        self.edit_observaciones.clear()
    
    def guardar_constantes(self):
        """
            Método para pasar al controlador la lista de objetos VO
            (constantes)
        """
        if self._paciente_activo is None:
            QMessageBox.warning(self, "Sin paciente", "No hay paciente activo. Vuelve al inicio y selecciona uno.")
            return
        
        if not self._constantes_pendientes:
            QMessageBox.warning(self, "Sin registros", "Añade al menos una constante")
            return
        
      
        
        # texto que aparecerá en el mensaje informativo
        resumen = '\n'.join(f" · {c['tipo']}: {c['valor']}" for c in self._constantes_pendientes)
        
        respuesta = QMessageBox.question(
            self, "Confirmar registros",
            f"Se van a guardar las siguientes constantes para {self._paciente_activo.nombre_completo}:\n\n{resumen}\n\n¿Deseas continuar?",
            QMessageBox.Ok | QMessageBox.Cancel )

        if respuesta == QMessageBox.Ok:

            # creamos la lista de objetos ConstantesVO
            lista_vos = [
            ConstantesVO(c['tipo'], c['valor'], c.get('observaciones', ''), self._enfermero.id_empleado,
                         self._paciente_activo.id_ingreso)
            for c in self._constantes_pendientes
            ]

            #pasamos la lista al controlador
            if self._controlador:

                print(f"({self._enfermero.id_empleado})Le paso al controlador la lista de constantes. ")
                self._controlador.guardar_constante(lista_vos)

            self._constantes_pendientes.clear()
            self._actualizar_tabla_pendientes()
    
    

    def _actualizar_tabla_pendientes(self):
        self.tabla_pendientes.setRowCount(len(self._constantes_pendientes))
        for fila, c in enumerate(self._constantes_pendientes):
            
            
            item0 = QTableWidgetItem(c["tipo"])
            item0.setTextAlignment(Qt.AlignCenter)
            self.tabla_pendientes.setItem(fila, 0, item0)
            
            
            item1 = QTableWidgetItem(c["valor"])
            item1.setTextAlignment(Qt.AlignCenter)
            self.tabla_pendientes.setItem(fila, 1, item1)
            
           
            item2 = QTableWidgetItem(c.get('observaciones', ''))
            self.tabla_pendientes.setItem(fila, 2, item2) 

    def _borrar_todo(self):
        self._constantes_pendientes.clear()
        self._actualizar_tabla_pendientes()
    
    def _borrar_seleccionado(self):
        fila = self.tabla_pendientes.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Sin selección", "Selecciona una constante para eliminar.")
            return
        self._constantes_pendientes.pop(fila)
        self._actualizar_tabla_pendientes()

    # ------------------------------------------------
    # Ver histórico de constantes
    # ------------------------------------------------

    def ver_historico(self):
        if self._paciente_activo is None:
            QMessageBox.warning(self, "Sin paciente", "Selecciona un paciente primero.")
            return

        dialogo = DialogoHistorico(self._paciente_activo, parent=self)

        # Ejecutamos el método del controladorEnfermeros que cambia la referencias a la vista
        # (de VentanaEnfermeros a DialogoHistorico)

        if self._controlador:
            self._controlador.set_dialogo_historico(dialogo)
        
        # Decimos a la ventana de diálogo que su controlodar es el mismo que el de 
        # VentanaEnfermeros (ControladorEnfermeros)
        dialogo.controlador = self._controlador

        dialogo.exec_() # DUDA: ejecutamos esto aquí, o desde ControladorEnfermeros?




    # ---------------------------------------------------------------------------------------------------------------------------------------------------------------
    #                                                                            CONTROLADOR 
    # --------------------------------------------------------------------------------------------------------------------------------------------------------------
    @property
    def controlador(self):
        return self._controlador

    @controlador.setter
    def controlador(self, ref_controlador):
        self._controlador = ref_controlador



