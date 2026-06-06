from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem
from PyQt5.QtCore import Qt


class LogicaMedicamentos:
    """
    Mixin de lógica de vista para CU7: Pedir Medicamentos.
    Se mezcla en VentanaAdministrativos junto con LogicaCitas y LogicaCredenciales.
    """

    def _init_medicamentos(self):
        """
        Conecta todas las señales de la página de medicamentos.
        Llamar desde __init__ de VentanaAdministrativos.
        """
        # Búsqueda en tiempo real sobre el catálogo
        self.search_medicamento.textChanged.connect(self._filtrar_catalogo)

        # Añadir medicamento seleccionado al pedido
        self.btn_anadir_al_pedido.clicked.connect(self._anadir_al_pedido)

        # Quitar una línea del pedido
        self.btn_borrar_seleccionado.clicked.connect(self._quitar_seleccionado)

        # Vaciar todo el pedido
        self.btn_borrar_todo.clicked.connect(self._vaciar_pedido)

        # Estilo coherente con los botones secundarios grises del resto de pestañas
        # (btn_limpiar_formulario, btn_cancelar, btn_limpiar_cita, etc.)
        _estilo_gris = (
            "QPushButton {"
            "    background-color: #dfe6e9;"
            "    color: #2d3436;"
            "    border: none;"
            "    border-radius: 8px;"
            "    padding: 8px 18px;"
            "    font-family: 'Segoe UI Semibold';"
            "    font-size: 13px;"
            "}"
            "QPushButton:hover { background-color: #b2bec3; }"
        )
        self.btn_borrar_seleccionado.setStyleSheet(_estilo_gris)
        self.btn_borrar_todo.setStyleSheet(_estilo_gris)

        # Confirmar pedido
        self.btn_confirmar_pedido.clicked.connect(self._confirmar_pedido)

        # Cache del catálogo completo para filtrado local
        self._catalogo_completo = []

        # Diccionario del pedido: {id_medicamento: (nombre, cantidad, unidad)}
        self._pedido = {}

    # ── Carga inicial del catálogo ────────────────────────────────────────────

    def cargar_catalogo_medicamentos(self, medicamentos):
        """
        Recibe la lista de MedicamentoVO del controlador y rellena la tabla del catálogo.
        También guarda la caché local para el filtrado.
        """
        self._catalogo_completo = medicamentos
        self._rellenar_tabla_catalogo(medicamentos)

    def _rellenar_tabla_catalogo(self, medicamentos):
        tabla = self.tabla_catalogo_medicamentos
        tabla.setRowCount(0)

        for med in medicamentos:
            fila = tabla.rowCount()
            tabla.insertRow(fila)

            tabla.setItem(fila, 0, QTableWidgetItem(str(med.id_medicamento)))
            tabla.setItem(fila, 1, QTableWidgetItem(med.nombre))

            # Mostrar stock con advertencia visual si está por debajo del mínimo
            item_stock = QTableWidgetItem(str(med.stock))
            if med.stock <= med.stock_minimo:
                item_stock.setForeground(Qt.red)
                item_stock.setToolTip("⚠ Stock por debajo del mínimo")
            tabla.setItem(fila, 2, item_stock)

            tabla.setItem(fila, 3, QTableWidgetItem(med.unidad_medida))

        tabla.horizontalHeader().setStretchLastSection(True)

    # ── Filtrado local del catálogo ───────────────────────────────────────────

    def _filtrar_catalogo(self, texto):
        """Filtra el catálogo localmente a medida que el usuario escribe."""
        if not texto.strip():
            self._rellenar_tabla_catalogo(self._catalogo_completo)
            return

        texto_lower = texto.lower()
        filtrados = [
            m for m in self._catalogo_completo
            if texto_lower in m.nombre.lower()
            or texto_lower in str(m.id_medicamento)
        ]
        self._rellenar_tabla_catalogo(filtrados)

        # Flujo alternativo CU7-3a: medicamento no encontrado
        if not filtrados:
            self.tabla_catalogo_medicamentos.setRowCount(1)
            item = QTableWidgetItem("No se encontraron resultados para la búsqueda.")
            item.setForeground(Qt.gray)
            self.tabla_catalogo_medicamentos.setItem(0, 1, item)

    # ── Gestión del pedido ────────────────────────────────────────────────────

    def _anadir_al_pedido(self):
        """Añade la fila seleccionada del catálogo al pedido con la cantidad indicada."""
        fila = self.tabla_catalogo_medicamentos.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Sin selección",
                                "Selecciona primero un medicamento del catálogo.")
            return

        id_item = self.tabla_catalogo_medicamentos.item(fila, 0)
        if id_item is None or not id_item.text().isdigit():
            return  # Fila de "no resultados", ignorar

        id_med   = int(id_item.text())
        nombre   = self.tabla_catalogo_medicamentos.item(fila, 1).text()
        unidad   = self.tabla_catalogo_medicamentos.item(fila, 3).text()
        cantidad = self.spin_cantidad.value()

        # Si ya existe en el pedido, acumulamos cantidad
        if id_med in self._pedido:
            _, cant_anterior, _ = self._pedido[id_med]
            cantidad += cant_anterior

        self._pedido[id_med] = (nombre, cantidad, unidad)
        self._refrescar_tabla_pedido()

    def _quitar_seleccionado(self):
        """Elimina la línea seleccionada de la tabla del pedido."""
        fila = self.tabla_pedido.currentRow()
        if fila < 0:
            return

        id_item = self.tabla_pedido.item(fila, 0)
        if id_item is None:
            return

        # Buscamos el id_medicamento por nombre en el pedido
        nombre_seleccionado = id_item.text()
        id_a_borrar = None
        for id_med, (nombre, _, _) in self._pedido.items():
            if nombre == nombre_seleccionado:
                id_a_borrar = id_med
                break

        if id_a_borrar is not None:
            del self._pedido[id_a_borrar]
            self._refrescar_tabla_pedido()

    def _vaciar_pedido(self):
        """Vacía todo el pedido actual."""
        if not self._pedido:
            return
        respuesta = QMessageBox.question(
            self, "Vaciar pedido",
            "¿Seguro que quieres eliminar todas las líneas del pedido?",
            QMessageBox.Yes | QMessageBox.No
        )
        if respuesta == QMessageBox.Yes:
            self._pedido.clear()
            self._refrescar_tabla_pedido()

    def _refrescar_tabla_pedido(self):
        """Sincroniza el diccionario _pedido con la tabla visual."""
        tabla = self.tabla_pedido
        tabla.setRowCount(0)

        for id_med, (nombre, cantidad, unidad) in self._pedido.items():
            fila = tabla.rowCount()
            tabla.insertRow(fila)
            tabla.setItem(fila, 0, QTableWidgetItem(nombre))
            tabla.setItem(fila, 1, QTableWidgetItem(str(cantidad)))
            tabla.setItem(fila, 2, QTableWidgetItem(unidad))

        # Habilitar/deshabilitar el botón de confirmar según si hay líneas
        self.btn_confirmar_pedido.setEnabled(len(self._pedido) > 0)

    # ── Confirmación del pedido ───────────────────────────────────────────────

    def _confirmar_pedido(self):
        """Delega la confirmación al controlador y limpia si hay éxito."""
        if not self._pedido:
            return
        self._controlador.confirmar_pedido(dict(self._pedido))

    def confirmar_pedido_exitoso(self):
        """Llamado por el controlador cuando el pedido se ha guardado correctamente."""
        QMessageBox.information(
            self, "Pedido confirmado",
            "El pedido se ha registrado correctamente."
        )
        self._pedido.clear()
        self._refrescar_tabla_pedido()
        self.search_medicamento.clear()
        self.spin_cantidad.setValue(1)

    # ── Helpers reutilizables ─────────────────────────────────────────────────

    def mostrar_error(self, titulo, mensaje):
        QMessageBox.warning(self, titulo, mensaje)

    def mostrar_info(self, titulo, mensaje):
        QMessageBox.information(self, titulo, mensaje)