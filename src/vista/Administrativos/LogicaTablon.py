# Mixin de vista para el Tablón de Tareas (página de inicio del administrativo).
# VentanaAdministrativos hereda de esta clase.

from PyQt5.QtWidgets import (
    QListWidgetItem, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QSizePolicy
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QColor


# Color de acento por rol
ROL_COLORES = {
    'medico':     ('#e8f4fd', '#6a9edb', '👨‍⚕️'),
    'médico':     ('#e8f4fd', '#6a9edb', '👨‍⚕️'),
    'enfermero':  ('#f0faf6', '#00b894', '🩺'),
    'enfermera':  ('#f0faf6', '#00b894', '🩺'),
}
ROL_DEFAULT = ('#fdf6e8', '#e67e22', '👤')


def _colores_rol(rol):
    if not rol:
        return ROL_DEFAULT
    return ROL_COLORES.get(rol.lower().strip(), ROL_DEFAULT)


class _TarjetaTarea(QWidget):
    """
    Widget visual para una tarea individual dentro del QListWidget.
    Muestra: icono de rol | remitente + fecha/hora | mensaje | botón ✓
    """

    def __init__(self, id_tarea, remitente, rol, mensaje, fecha, hora,
                 on_marcar, parent=None):
        super().__init__(parent)
        self._id_tarea = id_tarea
        self._on_marcar = on_marcar

        fondo, borde, icono = _colores_rol(rol)
        hora_str = str(hora)[:5]

        self.setStyleSheet(f"""
            QWidget#tarjeta {{
                background-color: {fondo};
                border: 1.5px solid {borde};
                border-radius: 10px;
            }}
        """)
        self.setObjectName("tarjeta")

        root = QHBoxLayout(self)
        root.setContentsMargins(12, 10, 12, 10)
        root.setSpacing(12)

        # Icono de rol
        lbl_icono = QLabel(icono)
        lbl_icono.setFont(QFont("Segoe UI", 22))
        lbl_icono.setFixedWidth(36)
        lbl_icono.setAlignment(Qt.AlignCenter)
        root.addWidget(lbl_icono)

        # Bloque central: cabecera + mensaje
        centro = QVBoxLayout()
        centro.setSpacing(4)

        cabecera = QHBoxLayout()
        cabecera.setSpacing(8)

        lbl_remitente = QLabel(remitente)
        lbl_remitente.setStyleSheet(
            f"font-family: 'Segoe UI Semibold'; font-size: 13px; color: {borde};"
        )
        cabecera.addWidget(lbl_remitente)

        lbl_rol = QLabel(f"· {rol}")
        lbl_rol.setStyleSheet(
            "font-family: 'Segoe UI'; font-size: 11px; color: #636e72;"
        )
        cabecera.addWidget(lbl_rol)
        cabecera.addStretch()

        lbl_fecha = QLabel(f"{fecha}  {hora_str}")
        lbl_fecha.setStyleSheet(
            "font-family: 'Segoe UI'; font-size: 11px; color: #b2bec3;"
        )
        cabecera.addWidget(lbl_fecha)
        centro.addLayout(cabecera)

        lbl_mensaje = QLabel(mensaje)
        lbl_mensaje.setWordWrap(True)
        lbl_mensaje.setStyleSheet(
            "font-family: 'Segoe UI'; font-size: 13px; color: #2d3436;"
        )
        centro.addWidget(lbl_mensaje)
        root.addLayout(centro)

        # Botón ✓ marcar hecha
        btn = QPushButton("✓ Hecho")
        btn.setFixedWidth(80)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {borde};
                color: white;
                border-radius: 8px;
                padding: 6px 10px;
                font-family: 'Segoe UI Semibold';
                font-size: 12px;
            }}
            QPushButton:hover {{ background-color: #00a381; }}
        """)
        btn.clicked.connect(lambda: self._on_marcar(self._id_tarea))
        root.addWidget(btn)


class LogicaTablon:

    def _init_tablon(self):
        """
        Conecta los widgets del tablón.
        Llamar desde __init__ de VentanaAdministrativos.
        """
        self.btn_refrescar_tablon.clicked.connect(self._on_refrescar)
        self.btn_marcar_hecha.setVisible(False)   # ocultamos el botón global; cada tarjeta tiene el suyo

    # ── Handlers ─────────────────────────────────────────────────────────────

    def _on_refrescar(self):
        if self._controlador:
            self._controlador.cargar_tareas()

    def _on_marcar_tarea(self, id_tarea):
        if self._controlador:
            self._controlador.marcar_tarea_hecha(id_tarea)

    # ── Métodos llamados por el controlador ───────────────────────────────────

    def cargar_tareas(self, filas):
        """
        Rellena list_tablon con tarjetas visuales.
        filas: lista de tuplas (id_tarea, nombre_remitente, rol_remitente, mensaje, fecha, hora)
        """
        self.list_tablon.clear()

        # Actualizar contador en el título del groupBox
        n = len(filas)
        titulo = "Tareas pendientes" if n == 0 else f"Tareas pendientes  ({n})"
        self.groupBox_tablon.setTitle(titulo)

        if not filas:
            item = QListWidgetItem("No hay tareas pendientes. Todo al día.")
            item.setFlags(item.flags() & ~Qt.ItemIsSelectable)
            item.setForeground(QColor("#b2bec3"))
            font = QFont("Segoe UI", 13)
            font.setItalic(True)
            item.setFont(font)
            item.setTextAlignment(Qt.AlignCenter)
            self.list_tablon.addItem(item)
            return

        for f in filas:
            id_tarea, remitente, rol, mensaje, fecha, hora = f

            tarjeta = _TarjetaTarea(
                id_tarea, remitente, rol, mensaje, fecha, hora,
                on_marcar=self._on_marcar_tarea,
                parent=self.list_tablon
            )

            item = QListWidgetItem(self.list_tablon)
            item.setSizeHint(QSize(0, tarjeta.sizeHint().height() + 12))
            item.setFlags(item.flags() & ~Qt.ItemIsSelectable)
            self.list_tablon.addItem(item)
            self.list_tablon.setItemWidget(item, tarjeta)

    def confirmar_tarea_eliminada(self):
        """Llamado por el controlador tras eliminar con éxito."""
        self._on_refrescar()