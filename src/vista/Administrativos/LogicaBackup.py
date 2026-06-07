# Mixin de vista para CU6 (Realizar Copia de Seguridad).
# VentanaAdministrativos hereda de esta clase.

from PyQt5.QtWidgets import QFileDialog, QMessageBox, QTableWidgetItem


class LogicaBackup:

    def _init_backup(self):
        """
        Conecta los widgets de la pestaña de backup.
        Llamar desde __init__ de VentanaAdministrativos.
        """
        self.btn_seleccionar_ruta.clicked.connect(self._on_seleccionar_ruta)
        self.btn_crear_backup.clicked.connect(self._on_crear_backup)
        self.progress_backup.setVisible(False)

    # ── Handlers de eventos ───────────────────────────────────────────────────

    def _on_seleccionar_ruta(self):
        """Abre el explorador de archivos para elegir el directorio de destino."""
        ruta = QFileDialog.getExistingDirectory(
            self,
            "Seleccionar directorio de destino",
            "",
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        if ruta:
            self.input_ruta_backup.setText(ruta)

    def _on_crear_backup(self):
        """Delega al controlador tras validar que hay ruta seleccionada."""
        ruta = self.input_ruta_backup.text().strip()
        if not ruta:
            QMessageBox.warning(self, "Sin ruta",
                                "Selecciona primero el directorio de destino.")
            return
        tipo = 'completa' if self.combo_tipo_backup.currentIndex() == 0 else 'bd'
        if self._controlador:
            self._controlador.crear_backup(ruta, tipo)

    # ── Métodos llamados por el controlador ───────────────────────────────────

    def mostrar_progreso_backup(self, visible):
        """Muestra u oculta la barra de progreso."""
        self.progress_backup.setVisible(visible)
        self.progress_backup.setRange(0, 0)   # modo indeterminado mientras trabaja

    def finalizar_progreso_backup(self):
        """Detiene la animación de la barra y la oculta."""
        self.progress_backup.setRange(0, 100)
        self.progress_backup.setValue(100)
        self.progress_backup.setVisible(False)

    def actualizar_ultima_copia(self, fecha, hora, usuario, tamanio_kb):
        """Actualiza el label de resumen con los datos de la última copia realizada."""
        tam = f"{tamanio_kb:,} KB" if tamanio_kb else "—"
        self.lbl_backup_sub.setText(
            f"Fecha: {fecha}   |   Hora: {hora}   |   "
            f"Realizada por: {usuario}   |   Tamaño: {tam}"
        )

    def cargar_historial_backup(self, filas):
        """
        Rellena tabla_historial_backup.
        filas: lista de tuplas (fecha, hora, tipo, tamanio_kb, realizado_por)
        """
        self.tabla_historial_backup.setRowCount(0)
        for f in filas:
            row = self.tabla_historial_backup.rowCount()
            self.tabla_historial_backup.insertRow(row)
            self.tabla_historial_backup.setItem(row, 0, QTableWidgetItem(str(f[0])))
            self.tabla_historial_backup.setItem(row, 1, QTableWidgetItem(str(f[1])))
            self.tabla_historial_backup.setItem(row, 2, QTableWidgetItem(str(f[2])))
            tam = f"{f[3]:,} KB" if f[3] else "—"
            self.tabla_historial_backup.setItem(row, 3, QTableWidgetItem(tam))
            self.tabla_historial_backup.setItem(row, 4, QTableWidgetItem(str(f[4])))
        self.tabla_historial_backup.resizeColumnsToContents()

    def habilitar_btn_backup(self, habilitado: bool):
        self.btn_crear_backup.setEnabled(habilitado)