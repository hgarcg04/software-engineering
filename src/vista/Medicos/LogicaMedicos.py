import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from PyQt5.QtWidgets import QMainWindow, QMessageBox, QInputDialog, QButtonGroup, QFileDialog
from PyQt5.QtCore import pyqtSignal, QTimer, QDateTime, Qt
from PyQt5 import uic
from PyQt5.QtGui import QPixmap
from datetime import datetime, timedelta


ui_path = os.path.join(os.path.dirname(__file__), "../Ui/VistaMedico.ui")
Form, Window = uic.loadUiType(ui_path)


class VentanaMedico(QMainWindow, Form):
    signal_logout = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._pacientes_busqueda = []
        self._ingresos_actuales = []
        self._citas_agenda_hoy = {}
        self._cita_activa = None
        self._controlador = None

        self.setupUi(self)

        # Reloj
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._actualizar_fecha_hora)
        self.timer.start(1000)
        self._actualizar_fecha_hora()

        # Botones de navegación exclusivos del menu
        self._btn_group = QButtonGroup(self)
        self._btn_group.setExclusive(True)
        self._btn_group.addButton(self.btn_nav_inicio)
        self._btn_group.addButton(self.btn_nav_agenda)
        self._btn_group.addButton(self.btn_nav_hcd)
        self._btn_group.addButton(self.btn_ingr)
        self._btn_group.addButton(self.btn_nav_neumonia)

        # Navegación sidebar
        self.btn_nav_inicio.clicked.connect(self._ir_inicio)
        self.btn_nav_agenda.clicked.connect(self._ir_agenda)
        self.btn_nav_hcd.clicked.connect(self._ir_hcd)
        self.btn_ingr.clicked.connect(self._ir_ingresos)
        self.btn_nav_neumonia.clicked.connect(self._ir_neumonia)

        # Inicio
        self.tabla_agenda_hoy.itemSelectionChanged.connect(self._on_cita_seleccionada)
        self.btn_iniciar_consulta.clicked.connect(self._abrir_consulta)
        self.btn_ver_hcd_inicio.clicked.connect(self._ver_hcd_paciente_agenda)

        # Consulta
        self.btn_volver_consulta.clicked.connect(self._ir_inicio)
        self.btn_abrir_receta.clicked.connect(self._abrir_dialogo_receta)
        self.btn_guardar_consulta.clicked.connect(self._guardar_consulta)
        self.btn_ingresar_paciente.clicked.connect(self._ingresar_paciente_cita)

        # Agenda completa
        self.calendario_agenda.selectionChanged.connect(self._on_fecha_calendario_cambiada)

        # HCD
        self.search_bar.textChanged.connect(self._buscar_paciente_hcd)
        self.tabla_busqueda_hcd.itemSelectionChanged.connect(self._on_paciente_hcd_seleccionado)
        self.tabla_episodios_hcd.itemSelectionChanged.connect(self._on_episodio_seleccionado)
        self.btn_cerrar_detalle.clicked.connect(self._cerrar_detalle_hcd)
        self.btn_dar_alta_hcd.clicked.connect(self._on_dar_alta_clicked)
        self.btn_ingresar_planta_hcd.clicked.connect(self._ingresar_paciente_hcd)

        # Ingresos
        self.btn_buscar_general.clicked.connect(self._buscar_en_ingresos)
        self.txt_buscar_general.returnPressed.connect(self._buscar_en_ingresos)
        self.tabla_ingresos.itemSelectionChanged.connect(self._on_ingreso_seleccionado)
        self.btn_añadir_tratamiento.clicked.connect(self._abrir_dialogo_receta_ingreso)
        self.btn_eliminar_tratamiento.clicked.connect(self._eliminar_tratamiento_ingreso)

        # Clasificación
        self.btn_seleccionar_rx.clicked.connect(self._seleccionar_imagen_rx)
        self.btn_analizar_rx.clicked.connect(self._analizar_rx)
        self._ruta_imagen_rx = None

        # Logout
        self.btn_logout.clicked.connect(self._logout)

    # -- Inicio --------------------------------------------------
    def _cargar_datos_iniciales(self):
        userVO = self._controlador._user_vo
        self.lbl_user_name.setText(f"Dr./Dra.: {userVO.nombre} {userVO.apellidos}")

    # ── Navegación ────────────────────────────────────────────── Se llaman con los botones del menú
    
    def _ir_inicio(self):
        self.stackedPanel.setCurrentIndex(0)
        self.btn_nav_inicio.setChecked(True)

    def _ir_agenda(self):
        self.stackedPanel.setCurrentIndex(1)
        self.btn_nav_agenda.setChecked(True)
        if self._controlador:
            self._controlador.cargar_agenda_completa()

    def _ir_hcd(self):
        self.stackedPanel.setCurrentIndex(2)
        self.btn_nav_hcd.setChecked(True)

    def _ir_ingresos(self):
        self.stackedPanel.setCurrentIndex(4)
        self.btn_ingr.setChecked(True)
        if self._controlador:
            self._controlador.cargar_ingresos()

    def _ir_neumonia(self):
        self.stackedPanel.setCurrentIndex(5)
        self.btn_nav_neumonia.setChecked(True)
    ##############################
    ##  Inicio / Agenda del día ##
    ##############################
    # Se llama desde el init
    def _actualizar_fecha_hora(self):
        self.lbl_datetime.setText(QDateTime.currentDateTime().toString("dd/MM/yyyy  HH:mm"))
    # Se llama desde ControladorMedicos._cargar_agenda_hoy()
    def cargar_agenda_hoy(self, lista_citas):
        self.tabla_agenda_hoy.setRowCount(0)
        self._citas_agendas_hoy = {} # Por si coincide que se pasa de día y no se reinicia, te imaginas? que guapo
        self.tabla_agenda_hoy.verticalHeader().setDefaultSectionSize(45) # Para establecer la altura de las filas
        self.tabla_agenda_hoy.verticalHeader().setVisible(False) # Para que no se vea el índice de la fila que no queda bien

        inicio = datetime.strptime("08:00", "%H:%M")
        fin = datetime.strptime("22:00", "%H:%M")
        hora_actual = datetime.now().strftime("%H:%M")
        slots = []
        actual = inicio
        while actual < fin:
            slots.append(actual.strftime("%H:%M"))
            actual += timedelta(minutes=30)

        for cita in lista_citas:
            hora_clave = str(cita.hora)[:5]
            self._citas_agenda_hoy[hora_clave] = cita

        for slot in slots:
            row = self.tabla_agenda_hoy.rowCount()
            self.tabla_agenda_hoy.insertRow(row)
            self.tabla_agenda_hoy.setItem(row, 0, self._item(slot))
            if slot in self._citas_agenda_hoy:
                cita_vo = self._citas_agenda_hoy[slot]
                self.tabla_agenda_hoy.setItem(row, 1, self._item(cita_vo.paciente_nombre))
                self.tabla_agenda_hoy.setItem(row, 2, self._item(cita_vo.motivo if cita.motivo else ""))
                for col in range(3):
                    self.tabla_agenda_hoy.item(row, col).setBackground(
                        __import__('PyQt5.QtGui', fromlist=['QColor']).QColor('#d8f3ed')
                    )
            else:
                self.tabla_agenda_hoy.setItem(row, 1, self._item(''))
                self.tabla_agenda_hoy.setItem(row, 2, self._item(''))

        self.tabla_agenda_hoy.resizeColumnsToContents()
    # Es una función de la tabla self.tabla_agenda_hoy
    def _on_cita_seleccionada(self):
        fila = self.tabla_agenda_hoy.currentRow()
        if fila < 0:
            self.btn_iniciar_consulta.setEnabled(False)
            self.btn_ver_hcd_inicio.setEnabled(False)
            return
        hora = self.tabla_agenda_hoy.item(fila, 0).text()[:5]
        tiene_cita = hora in self._citas_agenda_hoy
        self.btn_iniciar_consulta.setEnabled(tiene_cita)
        self.btn_ver_hcd_inicio.setEnabled(tiene_cita)
    # Es una función del botón self.btn_iniciar_consulta
    def _abrir_consulta(self):
        fila = self.tabla_agenda_hoy.currentRow()
        if fila < 0:
            return
        hora = self.tabla_agenda_hoy.item(fila, 0).text()[:5]
        if hora not in self._citas_agenda_hoy:
            return
        cita = self._citas_agenda_hoy[hora]
        if self._controlador:
            self._controlador.abrir_seleccion_episodio(cita)
    # Es una función del botón self.btn_ver_hcd_inicio
    def _ver_hcd_paciente_agenda(self):
        fila = self.tabla_agenda_hoy.currentRow()
        if fila < 0:
            return
        hora = self.tabla_agenda_hoy.item(fila, 0).text()[:5]
        if hora not in self._citas_agenda_hoy:
            return
        cita = self._citas_agenda_hoy[hora]
        self._ir_hcd()
        if self._controlador:
            self._controlador.cargar_hcd_desde_agenda(cita.id_paciente)
    # Se llama varias veces para configurar los botones de ingresar y alta
    def configurar_botones_hospitalizacion(self, puede_ingresar, puede_dar_alta):
        self.btn_ingresar_planta_hcd.setEnabled(puede_ingresar)
        self.btn_dar_alta_hcd.setEnabled(puede_dar_alta)
    # Se llama desde ControladorMedicos.exportar_informe_alta_pdf()
    def solicitar_ruta_informe_alta(self, nif_paciente):
        ruta, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar Informe de Alta Clínica",
            f"Informe_Alta_{nif_paciente}.pdf",
            "PDF Files (*.pdf)"
        )
        return ruta
    # Se llama varias veces para notificar desde el controlador
    def mostrar_notificacion(self, titulo, mensaje, es_error=False):
        """
        MÉTODO DE VISTA (MVC Puro): Muestra cuadros de diálogo de información o error.
        """
        from PyQt5.QtWidgets import QMessageBox
        
        if es_error:
            QMessageBox.critical(self, titulo, mensaje)
        else:
            QMessageBox.information(self, titulo, mensaje)
    # Se llama desde ControladorMedicos.abrir_seleccion_episodio()
    def abrir_pagina_consulta(self, cita_vo, episodio_vo=None):
        """
        Llamado por el controlador tras elegir episodio.
        Recibe la cita y opcionalmente el episodio seleccionado.
        """
        self._cita_activa = cita_vo
        self.lbl_cita_nombre.setText(cita_vo.paciente_nombre)
        self.lbl_cita_hora.setText(str(cita_vo.hora)[:5])
        self.lbl_cita_motivo.setText(cita_vo.motivo if cita_vo.motivo else '')

        if episodio_vo:
            # Episodio existente: pre-rellenar el diagnóstico previo como referencia
            self.edit_sintomas.clear()
            self.edit_diagnostico.setPlainText(
                f"[Continúa episodio del {str(episodio_vo.fecha_hora_inicio)[:10]}]\n"
            )
        else:
            self.edit_sintomas.clear()
            self.edit_diagnostico.clear()

        self.stackedPanel.setCurrentIndex(3)
    # Es una función del boton self.btn_añadir_tratamiento
    def _abrir_dialogo_receta(self):
        if self._controlador:
            self._controlador.abrir_receta(self._cita_activa)
    # Es una función del boton self.btn_guardar_consulta
    def _guardar_consulta(self):
        if self._controlador:
            self._controlador.guardar_consulta(
                sintomas=self.edit_sintomas.toPlainText(),
                diagnostico=self.edit_diagnostico.toPlainText(),
                tipo=self.combo_tipo_episodio.currentText(),
                cita=self._cita_activa
            )
        self._ir_inicio()
    # Es una función del botón self.btn_ingresar_paciente
    def _ingresar_paciente_cita(self):
        if self._cita_activa.hospitalizado:
            QMessageBox.warning(self, "Operación inválida",
                f"El paciente {self._cita_activa.paciente_nombre} ya está hospitalizado.")
            return

        respuesta = QMessageBox.question(
            self, "Confirmar ingreso",
            f"Se va a ingresar al siguiente paciente: {self._cita_activa.paciente_nombre}\n\n¿Deseas continuar?",
            QMessageBox.Ok | QMessageBox.Cancel)

        if respuesta == QMessageBox.Ok:
            habitacion, ok = QInputDialog.getText(
                self, "Ingreso de Paciente", "Escriba la habitación del ingresado:")
            if ok and habitacion.strip():
                if self._controlador:
                    self._controlador.ingresar_paciente(
                        self._cita_activa.id_paciente, habitacion.strip())
            elif ok:
                self.mostrar_notificacion(
                    "Campo Obligatorio", "Debe introducir una habitación.", es_error=True)

    #####################
    ## Agenda completa ##
    #####################
    # Se llama desde self.calendario_agenda_completa
    def _on_fecha_calendario_cambiada(self):
        if self._controlador:
            fecha = self.calendario_agenda.selectedDate()
            desde = fecha.toString('yyyy-MM-dd')
            self._controlador.cargar_agenda_completa(desde=desde, hasta=desde)
    # Se llama desde ControladorMedicos.cargar_agenda_completa que coge los datos del modelo
    def cargar_agenda_completa(self, lista_citas):
        self.tabla_agenda.setRowCount(0)
        for cita in lista_citas:
            row = self.tabla_agenda.rowCount()
            self.tabla_agenda.insertRow(row)
            self.tabla_agenda.setItem(row, 0, self._item(f"{str(cita.fecha)} {str(cita.hora)[:5]}")) # Cambiar esto porque ahora están separados
            self.tabla_agenda.setItem(row, 1, self._item(cita.paciente_nombre))
            self.tabla_agenda.setItem(row, 2, self._item(cita.motivo))
        self.tabla_agenda.resizeColumnsToContents()

    #####################
    ##       HCD       ##
    #####################
    # Se llama desde self.search_bar
    def _buscar_paciente_hcd(self, texto):
        if self._controlador:
            self._controlador.buscar_paciente_hcd(texto)
    # Se llama desde self.btn_ingresar_planta_hcd
    def _ingresar_paciente_hcd(self):
        paciente = self._pacientes_busqueda[self.tabla_busqueda_hcd.currentRow()]
        respuesta = QMessageBox.question(
            self, "Confirmar ingreso",
            f"Se va a ingresar al siguiente paciente: {paciente.nombre}\n\n¿Deseas continuar?",
            QMessageBox.Ok | QMessageBox.Cancel)

        if respuesta == QMessageBox.Ok:
            habitacion, ok = QInputDialog.getText(
                self, "Ingreso de Paciente", "Escriba la habitación del ingresado:")
            if ok and habitacion.strip():
                if self._controlador:
                    self._controlador.ingresar_paciente_desde_hcd(paciente.id_paciente, habitacion.strip())
            elif ok:
                self.mostrar_notificacion(
                    "Campo Obligatorio", "Debe introducir una habitación.", es_error=True)
    # Se llama desde self.btn_dar_alta_hcd
    def _on_dar_alta_clicked(self):
        if not self._controlador:
            return
        diagnostico_alta, ok = QInputDialog.getMultiLineText(
            self, 
            "Formulario de Alta Clínica", 
            "Escriba el diagnóstico de alta, tratamiento recomendado y observaciones finales:"
        )
        if ok and diagnostico_alta.strip():
            self._controlador.dar_alta_paciente(diagnostico_alta.strip())
        elif ok:
            self.mostrar_notificacion(
                "Campo Obligatorio", 
                "Debe introducir un diagnóstico o resumen clínico para poder tramitar el alta.", 
                es_error=True
            )
    # Se llama desde ControladorMedicos.buscar_paciente_hcd() que los ha conseguido desde el modelo
    def cargar_resultados_busqueda_hcd(self, lista_pacientes):
        self._pacientes_busqueda = lista_pacientes
        self.tabla_busqueda_hcd.setRowCount(0)
        for paciente in lista_pacientes:
            row = self.tabla_busqueda_hcd.rowCount()
            self.tabla_busqueda_hcd.insertRow(row)
            self.tabla_busqueda_hcd.setItem(row, 0, self._item(paciente.nif))
            self.tabla_busqueda_hcd.setItem(row, 1, self._item(paciente.nombre_completo))
            self.tabla_busqueda_hcd.setItem(row, 2, self._item(str(paciente.fecha_nacimiento)))
        self.tabla_busqueda_hcd.resizeColumnsToContents()
    # Se llama desde la tabla self.tabla_busqueda_hcd
    def _on_paciente_hcd_seleccionado(self):
        fila = self.tabla_busqueda_hcd.currentRow()
        if fila < 0 or not self._controlador:
            return
        paciente = self._pacientes_busqueda[fila]
        self._controlador.cargar_episodios_paciente(paciente)
    # Se llama desde ControladorMedicos.cargar_episodios_paciente() que los obtiene desde el modelo
    def cargar_episodios_hcd(self, paciente_nombre, lista_episodios):
        self.lbl_paciente_sel_nombre.setText(paciente_nombre)
        self.tabla_episodios_hcd.setRowCount(0)
        for ep in lista_episodios:
            row = self.tabla_episodios_hcd.rowCount()
            self.tabla_episodios_hcd.insertRow(row)
            self.tabla_episodios_hcd.setItem(row, 0, self._item(ep.fecha_hora_inicio))
            self.tabla_episodios_hcd.setItem(row, 1, self._item(ep.tipo))
            self.tabla_episodios_hcd.setItem(row, 2, self._item(ep.diagnostico))
        self.tabla_episodios_hcd.resizeColumnsToContents()
    # Se llama desde la tabla self.tabla_episodios_hcd
    def _on_episodio_seleccionado(self):
        fila = self.tabla_episodios_hcd.currentRow()
        if fila < 0 or not self._controlador:
            return
        self._controlador.cargar_detalle_episodio(fila)
    # Se llama desde ControladorMedicos.cargar_detalle_episodio tras haber accedido a la Base de Datos
    def mostrar_detalle_episodio(self, texto, lista_tratamientos):
        self.txt_detalle_episodio.setPlainText(texto)
        self.tabla_tratamientos_hcd.setRowCount(0)
        for t in lista_tratamientos:
            row = self.tabla_tratamientos_hcd.rowCount()
            self.tabla_tratamientos_hcd.insertRow(row)
            self.tabla_tratamientos_hcd.setItem(row, 0, self._item(t.get('medicamento', '')))
            self.tabla_tratamientos_hcd.setItem(row, 1, self._item(t.get('dosis', '')))
            self.tabla_tratamientos_hcd.setItem(row, 2, self._item(t.get('frecuencia', '')))
            self.tabla_tratamientos_hcd.setItem(row, 3, self._item(t.get('via', '')))
        self.tabla_tratamientos_hcd.resizeColumnsToContents()
    # Se llama desde el boton self.btn_cerrar_detalle
    def _cerrar_detalle_hcd(self):
        self.txt_detalle_episodio.clear()
        self.tabla_tratamientos_hcd.setRowCount(0)
        self.btn_ingresar_planta_hcd.setEnabled(False)
        self.btn_dar_alta_hcd.setEnabled(False)

    #####################
    ##     Ingreso     ##
    #####################
    # LLamado desde ControladorMedicos.cargar_ingresos() que consigue los ingresados y los altas recientes de la BD
    def cargar_ingresos(self, lista_ingresos, lista_altas):
        self._ingresos_actuales = lista_ingresos
        # Tabla ingresos actuales
        self.tabla_ingresos.setRowCount(0)
        self.tabla_ingresos.verticalHeader().setVisible(False)
        for ingresoVO in lista_ingresos:
            row = self.tabla_ingresos.rowCount()
            self.tabla_ingresos.insertRow(row)
            self.tabla_ingresos.setItem(row, 0, self._item(ingresoVO.id_ingreso))  # id_ingreso
            self.tabla_ingresos.setItem(row, 1, self._item(ingresoVO.habitacion or ""))  # habitacion/cama
            self.tabla_ingresos.setItem(row, 2, self._item(ingresoVO.nombre_completo))  # nombre
            self.tabla_ingresos.setItem(row, 3, self._item(ingresoVO.fecha_inicio))  # fecha
        self.tabla_ingresos.resizeColumnsToContents()

        # Tabla altas recientes
        self.tabla_altas_recientes.setRowCount(0)
        self.tabla_altas_recientes.verticalHeader().setVisible(False)
        for altaVO in lista_altas:
            row = self.tabla_altas_recientes.rowCount()
            self.tabla_altas_recientes.insertRow(row)
            self.tabla_altas_recientes.setItem(row, 0, self._item(altaVO.id_ingreso))  # id_ingreso
            self.tabla_altas_recientes.setItem(row, 1, self._item(altaVO.nombre_completo))  # nombre
            self.tabla_altas_recientes.setItem(row, 2, self._item(altaVO.fecha_inicio))  # fecha ingreso
            self.tabla_altas_recientes.setItem(row, 3, self._item(altaVO.fecha_fin))  # fecha alta
            self.tabla_altas_recientes.setItem(row, 4, self._item(altaVO.observaciones or ""))  # motivo
        self.tabla_altas_recientes.resizeColumnsToContents()
    # Llamado desde los botones self.btn_buscar_general y self.txt_buscar_general
    def _buscar_en_ingresos(self):
        texto = self.txt_buscar_general.text().strip()
        if self._controlador:
            self._controlador.filtrar_ingresos(texto)
    # Se llama desde la abla self.tabla_ingresos
    def _on_ingreso_seleccionado(self):
        fila = self.tabla_ingresos.currentRow()
        if fila < 0 or not self._controlador:
            return
        self.btn_añadir_tratamiento.setEnabled(True)
        self.btn_eliminar_tratamiento.setEnabled(False)
        self._controlador.cargar_tratamientos_ingreso(self._ingresos_actuales[fila])
    # LLamado desde ControladorMedicos.cargar_tratamientos_ingreso() con los datos obtenidos y este es llamado desde la función anterior
    def cargar_tratamientos_ingreso(self, lista_tratamientos, nombre_paciente):
        self.lbl_paciente_tratamiento.setText(nombre_paciente)
        self.tabla_tratamientos_ingreso.setRowCount(0)
        for t in lista_tratamientos:
            row = self.tabla_tratamientos_ingreso.rowCount()
            self.tabla_tratamientos_ingreso.insertRow(row)
            self.tabla_tratamientos_ingreso.setItem(row, 0, self._item(t.nombre or ''))
            self.tabla_tratamientos_ingreso.setItem(row, 1, self._item(t.dosis or ''))
            self.tabla_tratamientos_ingreso.setItem(row, 2, self._item(t.frecuencia or ''))
            self.tabla_tratamientos_ingreso.setItem(row, 3, self._item(t.via_administracion or ''))
            self.tabla_tratamientos_ingreso.setItem(row, 4, self._item(t.notas or ''))
        self.tabla_tratamientos_ingreso.resizeColumnsToContents()
        self.tabla_tratamientos_ingreso.itemSelectionChanged.connect(
            lambda: self.btn_eliminar_tratamiento.setEnabled(
                self.tabla_tratamientos_ingreso.currentRow() >= 0))
    # Se llama desde el boton self.btn_añadir_tratamiento
    def _abrir_dialogo_receta_ingreso(self):
        if self._controlador:
            self._controlador.abrir_receta_desde_ingreso()
    # Se llama desde el boton self.btn_eliminar_tratamiento
    def _eliminar_tratamiento_ingreso(self):
        fila = self.tabla_tratamientos_ingreso.currentRow()
        if fila < 0 or not self._controlador:
            return
        self._controlador.eliminar_tratamiento_ingreso(fila)
            
    ######################
    ##      MODELO      ##
    ######################
    # Se llama desde el boton self.btn_seleccionar_rx
    def _seleccionar_imagen_rx(self):
        ruta, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar radiografía", "",
            "Imágenes (*.png *.jpg *.jpeg)"
        )
        if ruta:
            self._ruta_imagen_rx = ruta
            pixmap = QPixmap(ruta).scaled(620, 520, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.lbl_imagen_rx.setPixmap(pixmap)
            self.btn_analizar_rx.setEnabled(True)
            self.frame_resultado_rx.setVisible(False)
    # Se llama desde el boton self.btn_analizar_rx
    def _analizar_rx(self):
        if self._ruta_imagen_rx:
            self.btn_analizar_rx.setEnabled(False)
            self.btn_analizar_rx.setText("Analizando...")
            self._controlador.clasificar_imagen(self._ruta_imagen_rx)
            self.btn_analizar_rx.setEnabled(True)
            self.btn_analizar_rx.setText("Analizar")
    # Se llama desde ControladorMedicos.clasificar_imagen() que lo hace en la lógica propia de neumonia
    def mostrar_resultado(self, label, confianza):
        self.frame_resultado_rx.setVisible(True)
        if "PNEUMONIA" in label.upper():
            self.lbl_resultado_rx.setText("⚠ NEUMONÍA\nDETECTADA")
            self.lbl_resultado_rx.setStyleSheet("font-family: 'Segoe UI Black'; font-size: 20px; color: #e17055;")
        else:
            self.lbl_resultado_rx.setText("✔ NORMAL")
            self.lbl_resultado_rx.setStyleSheet("font-family: 'Segoe UI Black'; font-size: 20px; color: #00b894;")
        self.lbl_confianza_rx.setText(f"Confianza: {confianza}%")
    # Muestra el error, esto es porque al principio me daba error con otros modelos
    def mostrar_error(self, mensaje):
        self.frame_resultado_rx.setVisible(True)
        self.lbl_resultado_rx.setText("Error al analizar la imagen")
        self.lbl_resultado_rx.setStyleSheet("font-family: 'Segoe UI Black'; font-size: 18px; color: #e17055;")
        self.lbl_confianza_rx.setText(mensaje)
    
###########################################################################################################    

    # ── Logout ───────────────────────────────────────────────────
    # Se llama desde el botón self.btn_logout
    def _logout(self):
        self.signal_logout.emit()
        self.close()

    # ── Utilidades ───────────────────────────────────────────────

    def _item(self, texto):
        from PyQt5.QtWidgets import QTableWidgetItem
        return QTableWidgetItem(str(texto))

    @property
    def controlador(self):
        return self._controlador

    @controlador.setter
    def controlador(self, ref):
        self._controlador = ref
        self._cargar_datos_iniciales()