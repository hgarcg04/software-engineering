import sys
import os


from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QButtonGroup, QMessageBox, QTableWidgetItem
from PyQt5.QtCore import QTimer, QDateTime, Qt, pyqtSignal
from PyQt5.QtWidgets import QHeaderView
from PyQt5.QtGui import QColor


from PyQt5.QtWidgets import QFileDialog
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, HRFlowable
from reportlab.lib import colors
from reportlab.lib.units import cm






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
        self.btn_nuevo_registro.clicked.connect(lambda: self._navegar(PAGE_CONSTANTES))
        self.btn_nav_medicacion.clicked.connect(self.actualizar_tomas_sesion_actual)
        self.btn_suministrar.clicked.connect(self.actualizar_tomas_sesion_actual)

        self.btn_nav_constantes.clicked.connect(lambda: self.edit_valor_constante.setFocus())
     
        self.btn_nav_medicacion.clicked.connect(lambda: self._navegar(PAGE_MEDICACION))
        self.btn_suministrar.clicked.connect(lambda: self._navegar(PAGE_MEDICACION))

        self.btn_nav_episodios.clicked.connect(lambda: self._navegar(PAGE_EPISODIOS))
        self.btn_ver_registros.clicked.connect(self._abrir_detalles_ingreso)
        self.btn_cerrar_detalles_ingreso.clicked.connect(lambda: self._navegar(PAGE_DETALLES))
        self.btn_nuevo_registro.clicked.connect(lambda: self.edit_valor_constante.setFocus())

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

        # --- PDF ----
        self.btn_exportar_pdf.clicked.connect(self.exportar_informe_pdf)

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
            self.btn_nav_episodios,
        ]
        for i, btn in enumerate(nav_btns):
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

        self._crear_pdf_informe(ruta, pac)
    
    def _crear_pdf_informe(self, ruta, pac):
        
        doc = SimpleDocTemplate(
            ruta,
            pagesize=A4,
            leftMargin=2*cm,
            rightMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
    

        historia = []
    
        # --- CABECERA ---
        cabecera_data = [[
            Paragraph("Informe de Hospitalización"),
        ]]
        tabla_cabecera = Table(cabecera_data, colWidths=[17*cm])

        
        historia.append(tabla_cabecera)
        historia.append(Spacer(1, 0.3*cm))
    
        ahora = QDateTime.currentDateTime().toString("dd/MM/yyyy HH:mm")
        historia.append(Paragraph(f"Documento generado el {ahora}"))
        historia.append(Spacer(1, 0.5*cm))
    
        # --- SECCIÓN: DATOS DEL PACIENTE ---
        historia.append(Paragraph("DATOS DEL PACIENTE"))
        historia.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#0cb868')))
        historia.append(Spacer(1, 0.2*cm))
    
        datos_paciente = [
            [Paragraph("NIF / DNI:"),       Paragraph(str(pac.nif)),
            Paragraph("Nombre completo:"),  Paragraph(f"{pac.nombre} {pac.apellido1} {pac.apellido2}")],
            [Paragraph("Fecha de nacimiento:"), Paragraph(str(pac.fecha_nacimiento)),
            Paragraph("Género:"),           Paragraph(str(pac.genero))],
        ]
        tabla_pac = Table(datos_paciente, colWidths=[4*cm, 4.5*cm, 4*cm, 4.5*cm])
        historia.append(tabla_pac)
        historia.append(Spacer(1, 0.5*cm))
    
        # --- SECCIÓN: DATOS DEL INGRESO ---
        historia.append(Paragraph("DATOS DEL INGRESO"))
        historia.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#0cb868')))
        historia.append(Spacer(1, 0.2*cm))
    
        fecha_ingreso = str(pac.fecha_inicio_ingreso)[:16] if pac.fecha_inicio_ingreso else "—"
        dieta = str(pac.dieta) if pac.dieta else "—"
    
        datos_ingreso = [
            [Paragraph("Habitación:"),      Paragraph(str(pac.num_habitacion)),
            Paragraph("Fecha de ingreso:"), Paragraph(fecha_ingreso)],
            [Paragraph("Médico asignado:"), Paragraph(str(pac.medico_asignado)),
            Paragraph("Dieta:"),            Paragraph(dieta)],
        ]
        tabla_ing = Table(datos_ingreso, colWidths=[4*cm, 4.5*cm, 4*cm, 4.5*cm])
        historia.append(tabla_ing)
        historia.append(Spacer(1, 1*cm))

        # --- OBSERVACIONES ---

        historia.append(Paragraph("ANOTACIONES AL INGRESAR"))
        historia.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#0cb868")))
        historia.append(Spacer(1, 0.2*cm))
        
        historia.append(Paragraph(str(pac.observaciones)))
    
    
        doc.build(historia)
    
        QMessageBox.information(self, "PDF exportado", f"Informe guardado correctamente en:\n{ruta}")



    
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
                print(f"({self._enfermero.id_empleado})Le paso al controlador la lista de constantes. ")
                self._controlador.guardar_constante(self._constantes_pendientes, self._enfermero.id_empleado, self._paciente_activo.id_ingreso)

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

        self.parpadear(10, True)
        self.edit_notas_toma.clear()

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

            

    # ---------------------------------------------------------------------------------------------------------------------------------------------------------------
    #                                                                            CONTROLADOR 
    # --------------------------------------------------------------------------------------------------------------------------------------------------------------
    @property
    def controlador(self):
        return self._controlador

    @controlador.setter
    def controlador(self, ref_controlador):
        self._controlador = ref_controlador



