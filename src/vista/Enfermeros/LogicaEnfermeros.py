import sys
import os


from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QTableWidgetItem, QTableWidget
from PyQt5.QtCore import QTimer, QDateTime, Qt, pyqtSignal
from PyQt5.QtWidgets import QHeaderView
from PyQt5.QtGui import QColor


from PyQt5.QtWidgets import QFileDialog


from src.vista.Enfermeros.LogicaDialogoConstantes import DialogoHistorico

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
ui_path = os.path.join(os.path.dirname(__file__), "../Ui/VistaEnfermero.ui")



PAGE_INICIO     = 0
PAGE_CONSTANTES = 1
PAGE_MEDICACION = 2
PAGE_DETALLES   = 3
PAGE_HCD        = 4




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
        self.btn_nuevo_registro.clicked.connect(lambda: self._navegar(PAGE_CONSTANTES))
        self.btn_nav_medicacion.clicked.connect(self.actualizar_tomas_sesion_actual)
        self.btn_suministrar.clicked.connect(self.actualizar_tomas_sesion_actual)



        self.btn_nav_constantes.clicked.connect(lambda: self.edit_valor_constante.setFocus())
     
        self.btn_nav_medicacion.clicked.connect(lambda: self._navegar(PAGE_MEDICACION))
        self.btn_suministrar.clicked.connect(lambda: self._navegar(PAGE_MEDICACION))

        self.btn_ver_registros.clicked.connect(self._abrir_detalles_ingreso)
        self.btn_cerrar_detalles_ingreso.clicked.connect(lambda: self._navegar(PAGE_DETALLES))
        self.btn_nuevo_registro.clicked.connect(lambda: self.edit_valor_constante.setFocus())

        self.btn_nav_hcd.clicked.connect(lambda: self._navegar(PAGE_HCD))
        self.btn_nav_hcd.clicked.connect(lambda: self.search_bar_hcd.clear())


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


        # --- Botones de pagina de medicación ---
        self.tabla_tratamientos.cellClicked.connect(self.on_tratamiento_clicked)
        self.btn_confirmar_toma.clicked.connect(self.on_confirmar_administracion_clicked)
        self.tabla_tomas_sesion.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla_tomas_sesion.setToolTip("Selecciona una fila y pulsa Supr para eliminar el registro.")

        # --- PDF ----
        self.btn_exportar_pdf.clicked.connect(self.exportar_informe_pdf)

        # --- Consultar HCD ------

        self.search_bar_hcd.textChanged.connect(self._buscar_paciente_hcd)
        self.tabla_busqueda_hcd.itemSelectionChanged.connect(self._on_paciente_hcd_seleccionado)
        self.tabla_episodios_hcd.itemSelectionChanged.connect(self._on_episodio_hcd_seleccionado)
        self.btn_cerrar_detalle_hcd.clicked.connect(self._cerrar_detalle_hcd)
        

        # -----------------------------------------------------------------------------
        # INICIALIZACIONES
        # -----------------------------------------------------------------------------

        self._todos_los_pacientes = [] 
        self._paciente_activo = None
        self._enfermero = None
        self._constantes_pendientes = []
        self._tratamiento_activo = None
        self._ultima_toma = None
        self._tomas_sesion_actual = []

        self._pacientes_hcd_busqueda = []
        self._episodios_hcd_actuales = []

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

    def cargar_ultima_toma(self, toma):
        self._ultima_toma = toma
    
    def cargar_tomas_sesion_actual(self, lista):
        self._tomas_sesion_actual = lista


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
            None,  # PAGE_DETALLES no tiene botón de nav
            self.btn_nav_hcd,
        ]
        for i, btn in enumerate(nav_btns):
            if btn is not None:
                btn.setChecked(i == indice)




    # ---------------------------------------------------------------------------------------------------------------------------------------------------
    #                                                                   PÁGINA DE INICIO
    # ---------------------------------------------------------------------------------------------------------------------------------------------------
  
    def mostrar_tabla_pacientes(self, lista):
        self.tabla_pacientes.setRowCount(len(lista))
        
        for fila, pac in enumerate(lista):
            fecha_inicio_ingreso = f"{pac.fecha_inicio_ingreso[:16]} {pac.hora_inicio_ingreso[:5]}" if pac.fecha_inicio_ingreso else "—"

            datos = [
                pac.nif,
                pac.nombre_completo,
                pac.num_habitacion,
                pac.medico_asignado,
                str(fecha_inicio_ingreso)
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
        self.controlador.cargar_tratamientos(self._paciente_activo)


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

        self.tabla_tratamientos.setRowCount(0)
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
    #                                                      PÁGINA DE INFORME INICIAL DE HOSPITALIZACIÓN
    # ----------------------------------------------------------------------------------------------------------------------------------------------------------


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
        self.lbl_det_fingreso.setText(str(pac.fecha_inicio_ingreso)[:16] if pac.fecha_inicio_ingreso else "—")
        self.lbl_det_medico.setText(str(pac.medico_asignado))
        self.lbl_det_dieta.setText(str(pac.dieta) if pac.dieta else "—")
        ahora = QDateTime.currentDateTime().toString("dd/MM/yyyy HH:mm")
        self.lbl_inf_fecha_gen.setText(f"Generado el: {ahora}")
        self.lbl_det_observaciones.setText(pac.observaciones)
    

    def exportar_informe_pdf(self):
        """
        Exporta el informe inicial de hospitalización del paciente activo a un PDF.
            
        """
        if self._paciente_activo is None:
            return
    
        pac = self._paciente_activo
    
        # Diálogo para elegir dónde guardar
        ruta, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar informe",
            f"Informe_inicio_hospitalizacion{pac.nif}.pdf",
            "PDF Files (*.pdf)"
        )
        if not ruta:
            return

        self.controlador.crear_pdf_informe(self, ruta, pac)
    
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
        
      
        
        # texto que aparecerá en el mensaje informativo antes de guardar
        resumen = '\n'.join(f" · {c['tipo']}: {c['valor']}" for c in self._constantes_pendientes)
        
        respuesta = QMessageBox.question(
            self, "Confirmar registros",
            f"Se van a guardar las siguientes constantes para {self._paciente_activo.nombre_completo}:\n\n{resumen}\n\n¿Deseas continuar?",
            QMessageBox.Ok | QMessageBox.Cancel )

        if respuesta == QMessageBox.Ok:
            #pasamos la lista al controlador
            if self._controlador:
                self._controlador.guardar_constante(self._constantes_pendientes, self._enfermero.id_empleado, self._paciente_activo.id_ingreso, )

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

        if self.controlador:
            self.controlador.set_dialogo_historico(dialogo)
        
        # Decimos a la ventana de diálogo que su controlodar es el mismo que el de 
        # VentanaEnfermeros (ControladorEnfermeros)
        dialogo.controlador = self._controlador

        dialogo.exec_() 

        # Cuando se deje de ejecutar el dialogo de historico
        # devolvemos la referencia de la vista a la ventana principal
        self.controlador.set_ventana_enfermeros(self)




    # ----------------------------------------------------------------------------------------------------------------------------------------------------------
    #                                                      PÁGINA DE SUMINISTRO DE MEDICACIÓN
    # ----------------------------------------------------------------------------------------------------------------------------------------------------------

    
    def mostrar_tratamientos(self, lista):
        self.tabla_tratamientos.setRowCount(len(lista))
        
        for fila, t in enumerate(lista):
            fecha_inicio = str(t.fecha_inicio)[:16] if t.fecha_inicio else "—"

            datos = [
                t.nombre, t.categoria, t.dosis, t.frecuencia, str(fecha_inicio)
            ]
            
            for col, valor in enumerate(datos):
                item = QTableWidgetItem(str(valor))
                item.setTextAlignment(Qt.AlignCenter)
                item.setData(Qt.UserRole, t)  
                self.tabla_tratamientos.setItem(fila, col, item)    
    
    def on_tratamiento_clicked(self, fila):

        self.btn_confirmar_toma.setEnabled(True)
        item = self.tabla_tratamientos.item(fila, 0)
        if item is None:
            return

        self._tratamiento_activo = item.data(Qt.UserRole)
        self.actualizar_ultima_toma()
        self.actualizar_tomas_sesion_actual()



        # Rellenamos los detalles
        self.lbl_det_inicio.setText(self._tratamiento_activo.fecha_inicio)
        self.lbl_det_fin.setText(self._tratamiento_activo.fecha_fin if self._tratamiento_activo.fecha_fin else "No indicada")
        self.lbl_det_medicamento.setText(self._tratamiento_activo.nombre)
        self.lbl_det_notas_medico.setText(f"{self._tratamiento_activo.notas} {self._tratamiento_activo.dosis}")
        self.lbl_det_frecuencia.setText(self._tratamiento_activo.frecuencia)
        self.lbl_det_via.setText(self._tratamiento_activo.via_administracion)
        

    def on_confirmar_administracion_clicked(self):

        observaciones = self.edit_notas_toma.toPlainText()
        self.controlador.guardar_nueva_toma(self._enfermero.id_empleado, self._tratamiento_activo.id_tratamiento, observaciones)
        self.controlador.actualizar_stock(self._tratamiento_activo.id_medicamento, -self._tratamiento_activo.dosis)

        self.actualizar_ultima_toma()
        self.actualizar_tomas_sesion_actual()

        self.parpadear(15, True)
        self.edit_notas_toma.clear()

    def confirmar_aviso(self):
        QMessageBox.warning(self, "Stock por debajo del umbral", "El medicamento suministrado se está agotando.\n"
                                                                 "Se ha dado aviso automático a personal administrativo.")




    def parpadear(self, n_veces, encendido):
        # Funcion para que el enfermero pueda ver que se ha registrado una nueva confirmación de 
        # administración de medicación.

        fila_nueva_toma = 0 # fila que va a parpadear

        if n_veces <= 0:
            # Cuando termina, quitar el color
            for columna in range(self.tabla_tomas_sesion.columnCount()):
                item = self.tabla_tomas_sesion.item(fila_nueva_toma, columna)
                if item:
                    item.setBackground(QColor("white"))
            return
        
        color = QColor("#c8f7e8") if encendido else QColor("white")
        for columna in range(self.tabla_tomas_sesion.columnCount()):
            item = self.tabla_tomas_sesion.item(fila_nueva_toma, columna)
            if item:
                item.setBackground(color)
        
        # definimos tiempo entre color y no color
        QTimer.singleShot(300, lambda: self.parpadear(n_veces - 1, not encendido)) 

        
    def actualizar_ultima_toma(self):
        if self._tratamiento_activo:
            self.controlador.obtener_ultima_toma(self._tratamiento_activo)
        if self._ultima_toma:
            self.lbl_det_ultima_toma.setText(f"{self._ultima_toma.fecha} - {self._ultima_toma.hora[:5]}")

    def actualizar_tomas_sesion_actual(self):
        if self._paciente_activo:
            self.controlador.obtener_tomas_sesion_actual(self._paciente_activo)
            self.tabla_tomas_sesion.setRowCount(len(self._tomas_sesion_actual))
            for fila, t in enumerate(self._tomas_sesion_actual):
                
                item0 = QTableWidgetItem(str(t.nombre))
                item0.setTextAlignment(Qt.AlignCenter)
                self.tabla_tomas_sesion.setItem(fila, 0, item0)
                
                
                item1 = QTableWidgetItem(t.hora)
                item1.setTextAlignment(Qt.AlignCenter)
                self.tabla_tomas_sesion.setItem(fila, 1, item1)
                
            
                item2 = QTableWidgetItem(t.observaciones)
                self.tabla_tomas_sesion.setItem(fila, 2, item2)

    # sobreescribimos el metodo de QWidget para recibir el evento de el botn 'supr' presionado
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            fila = self.tabla_tomas_sesion.currentRow()
            if fila >= 0:
                print("recibida señal de boton delete")

                respuesta = QMessageBox.question(
                    self, "Botón suprimir presionado",
                    f"Se va a eliminar el registro de la toma selecionada\n\n¿Deseas continuar?",
                    QMessageBox.Ok | QMessageBox.Cancel)

                if respuesta == QMessageBox.Ok:
                    toma = self._tomas_sesion_actual[fila]
                    self.controlador.eliminar_toma(toma.id_toma)
                    self.actualizar_tomas_sesion_actual()
                    self.actualizar_ultima_toma()
                    self.tabla_tomas_sesion.clearSelection()
                    #self.actualizar_ultima_toma()



    # ---------------------------------------------------------
    #   PÁGINA DE CONSULTAR HCD
    # ---------------------------------------------------------

    def _buscar_paciente_hcd(self, texto):
        if not texto or len(texto) < 2:
            self.tabla_busqueda_hcd.setRowCount(0)
            return
        if self._controlador:
            self._controlador.buscar_paciente_hcd(texto)

    def cargar_resultados_busqueda_hcd(self, lista_pacientes):
        self._pacientes_hcd_busqueda = lista_pacientes
        self.tabla_busqueda_hcd.setRowCount(0)
        for paciente in lista_pacientes:
            row = self.tabla_busqueda_hcd.rowCount()
            self.tabla_busqueda_hcd.insertRow(row)
            self.tabla_busqueda_hcd.setItem(row, 0, QTableWidgetItem(str(paciente.nif)))
            self.tabla_busqueda_hcd.setItem(row, 1, QTableWidgetItem(str(paciente.nombre_completo)))
            self.tabla_busqueda_hcd.setItem(row, 2, QTableWidgetItem(str(paciente.fecha_nacimiento)))
        self.tabla_busqueda_hcd.resizeColumnsToContents()

    def _on_paciente_hcd_seleccionado(self):
        fila = self.tabla_busqueda_hcd.currentRow()
        if fila < 0 or not self._controlador:
            return
        paciente = self._pacientes_hcd_busqueda[fila]
        self._controlador.cargar_episodios_hcd(paciente)

    def cargar_episodios_hcd(self, paciente_nombre, lista_episodios):
        self._episodios_hcd_actuales = lista_episodios
        self.lbl_paciente_sel_nombre_hcd.setText(paciente_nombre)
        self.tabla_episodios_hcd.setRowCount(0)
        for ep in lista_episodios:
            row = self.tabla_episodios_hcd.rowCount()
            self.tabla_episodios_hcd.insertRow(row)
            self.tabla_episodios_hcd.setItem(row, 0, QTableWidgetItem(str(ep.fecha_hora_inicio)))
            self.tabla_episodios_hcd.setItem(row, 1, QTableWidgetItem(str(ep.tipo)))
            self.tabla_episodios_hcd.setItem(row, 2, QTableWidgetItem(str(ep.diagnostico)))
        self.tabla_episodios_hcd.resizeColumnsToContents()

    def _on_episodio_hcd_seleccionado(self):
        fila = self.tabla_episodios_hcd.currentRow()
        if fila < 0 or not self._controlador:
            return
        self._controlador.cargar_detalle_episodio_hcd(fila)

    def mostrar_detalle_episodio_hcd(self, texto, lista_tratamientos):
        self.txt_detalle_episodio_hcd.setPlainText(texto)
        self.tabla_tratamientos_hcd.setRowCount(0)
        for t in lista_tratamientos:
            row = self.tabla_tratamientos_hcd.rowCount()
            self.tabla_tratamientos_hcd.insertRow(row)
            self.tabla_tratamientos_hcd.setItem(row, 0, QTableWidgetItem(str(t.get('medicamento', ''))))
            self.tabla_tratamientos_hcd.setItem(row, 1, QTableWidgetItem(str(t.get('dosis', ''))))
            self.tabla_tratamientos_hcd.setItem(row, 2, QTableWidgetItem(str(t.get('frecuencia', ''))))
            self.tabla_tratamientos_hcd.setItem(row, 3, QTableWidgetItem(str(t.get('via', ''))))
        self.tabla_tratamientos_hcd.resizeColumnsToContents()

    def _cerrar_detalle_hcd(self):
        self.txt_detalle_episodio_hcd.clear()
        self.tabla_tratamientos_hcd.setRowCount(0)

    # ---------------------------------------------------------------------------------------------------------------------------------------------------------------
    #                                                                            CONTROLADOR 
    # --------------------------------------------------------------------------------------------------------------------------------------------------------------
    @property
    def controlador(self):
        return self._controlador

    @controlador.setter
    def controlador(self, ref_controlador):
        self._controlador = ref_controlador



