# Mixin de vista para el Tablón de Tareas (página de inicio del administrativo).
# VentanaAdministrativos hereda de esta clase.

from PyQt5.QtWidgets import QListWidgetItem, QMessageBox
from PyQt5.QtCore import Qt


class LogicaTablon:

    def _init_tablon(self):
        """
        Conecta los widgets del tablón.
        Llamar desde __init__ de VentanaAdministrativos.
        """
        # id_tarea de la fila actualmente seleccionada
        self._id_tarea_seleccionada = None

        self.list_tablon.itemClicked.connect(self._on_tarea_seleccionada)
        self.btn_marcar_hecha.clicked.connect(self._on_marcar_hecha)
        self.btn_refrescar_tablon.clicked.connect(self._on_refrescar)

        # Deshabilitar "Marcar como hecha" hasta que haya selección
        self.btn_marcar_hecha.setEnabled(False)

    # ── Handlers ─────────────────────────────────────────────────────────────

    def _on_tarea_seleccionada(self, item):
        self._id_tarea_seleccionada = item.data(Qt.UserRole)
        self.btn_marcar_hecha.setEnabled(True)

    def _on_marcar_hecha(self):
        if self._id_tarea_seleccionada is None:
            return
        if self._controlador:
            self._controlador.marcar_tarea_hecha(self._id_tarea_seleccionada)

    def _on_refrescar(self):
        if self._controlador:
            self._controlador.cargar_tareas()

    # ── Métodos llamados por el controlador ───────────────────────────────────

    def cargar_tareas(self, filas):
        """
        Rellena list_tablon con las tareas pendientes.
        filas: lista de tuplas (id_tarea, nombre_remitente, rol_remitente, mensaje, fecha, hora)
        """
        self.list_tablon.clear()
        self._id_tarea_seleccionada = None
        self.btn_marcar_hecha.setEnabled(False)

        if not filas:
            item = QListWidgetItem("No hay tareas pendientes.")
            item.setFlags(item.flags() & ~Qt.ItemIsSelectable)
            self.list_tablon.addItem(item)
            return

        for f in filas:
            id_tarea, remitente, rol, mensaje, fecha, hora = f
            hora_str = str(hora)[:5]   # HH:MM
            texto = f"[{fecha}  {hora_str}]  {remitente} ({rol})\n{mensaje}"
            item = QListWidgetItem(texto)
            item.setData(Qt.UserRole, id_tarea)
            self.list_tablon.addItem(item)

    def confirmar_tarea_eliminada(self):
        """Llamado por el controlador tras eliminar con éxito. Refresca la lista."""
        self._id_tarea_seleccionada = None
        self.btn_marcar_hecha.setEnabled(False)
        if self._controlador:
            self._controlador.cargar_tareas()