from datetime import date, timedelta, datetime
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QFrame, QSizePolicy, QWidget
)
from PyQt5.QtCore import Qt, pyqtSignal, QDate
from PyQt5.QtGui import QFont, QColor


FRANJAS = [f"{h:02d}:{m:02d}" for h in range(8, 15) for m in (0, 30)
           if not (h == 14 and m == 30)]   # 08:00 … 14:00

COLOR_LIBRE    = "#d8f3ed"
COLOR_OCUPADA  = "#fde8e8"
COLOR_BLOQUEADA= "#e8e8e8"
COLOR_PASADA   = "#ececec"
COLOR_HOVER    = "#00b894"
BORDER_LIBRE   = "#00b894"
BORDER_OCUPADA = "#e17055"
BORDER_BLOQUEADA="#b2bec3"

DIAS_ES = ["Lun", "Mar", "Mié", "Jue", "Vie"]


class DialogCalendario(QDialog):
    # Emite (fecha:date, hora:str) cuando el usuario elige una celda libre
    hora_seleccionada = pyqtSignal(object, str)

    def __init__(self, id_medico, nombre_medico, fn_citas, fn_bloqueados, fecha_inicial=None, parent=None):
        super().__init__(parent)
        self._id_medico = id_medico
        self._nombre_medico = nombre_medico
        self._fn_citas = fn_citas
        self._fn_bloqueados = fn_bloqueados
        # Si se proporciona fecha_inicial, abrir en su semana; si no, usar hoy
        referencia = fecha_inicial if isinstance(fecha_inicial, date) else date.today()
        self._lunes = referencia - timedelta(days=referencia.weekday())
        self._hora_pendiente = None   # (fecha, hora) elegida pero aún sin confirmar
        self._btn_pendiente = None    # botón actualmente marcado como seleccionado

        self.setWindowTitle("Seleccionar hora de cita")
        self.setMinimumSize(900, 560)
        self.setModal(True)
        self._build_ui()
        self._cargar_semana()

    # ── Construcción del layout ───────────────────────────────────────────────

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setSpacing(12)
        root.setContentsMargins(20, 20, 20, 20)

        # Cabecera: médico + navegación de semana
        header = QHBoxLayout()
        self._lbl_titulo = QLabel()
        self._lbl_titulo.setFont(QFont("Segoe UI Black", 14))
        self._lbl_titulo.setStyleSheet("color: #2d3436;")
        header.addWidget(self._lbl_titulo)
        header.addStretch()

        btn_prev = QPushButton("◀  Semana anterior")
        btn_next = QPushButton("Semana siguiente  ▶")
        for btn in (btn_prev, btn_next):
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #6a9edb; color: white;
                    border-radius: 8px; padding: 6px 14px;
                    font-family: 'Segoe UI Semibold'; font-size: 13px;
                }
                QPushButton:hover { background-color: #4a7ec0; }
            """)
        btn_prev.clicked.connect(self._semana_anterior)
        btn_next.clicked.connect(self._semana_siguiente)
        header.addWidget(btn_prev)
        header.addWidget(btn_next)
        root.addLayout(header)

        # Leyenda
        leyenda = QHBoxLayout()
        for color, borde, texto in [
            (COLOR_LIBRE,     BORDER_LIBRE,     "Libre — haz clic para elegir"),
            (COLOR_OCUPADA,   BORDER_OCUPADA,   "Ocupada"),
            (COLOR_BLOQUEADA, BORDER_BLOQUEADA, "Bloqueada"),
        ]:
            cuadro = QLabel()
            cuadro.setFixedSize(16, 16)
            cuadro.setStyleSheet(f"background:{color}; border:1.5px solid {borde}; border-radius:3px;")
            lbl = QLabel(texto)
            lbl.setStyleSheet("font-family:'Segoe UI'; font-size:12px; color:#636e72;")
            leyenda.addWidget(cuadro)
            leyenda.addWidget(lbl)
            leyenda.addSpacing(16)
        leyenda.addStretch()
        root.addLayout(leyenda)

        # Grid del calendario
        self._grid_widget = QWidget()
        self._grid = QGridLayout(self._grid_widget)
        self._grid.setSpacing(4)
        root.addWidget(self._grid_widget)

        # Footer: botón OK (deshabilitado hasta elegir hora) + Cancelar
        self._btn_ok = QPushButton("Confirmar hora")
        self._btn_ok.setEnabled(False)
        self._btn_ok.setStyleSheet("""
            QPushButton {
                background-color: #00b894; color: white;
                border-radius: 8px; padding: 8px 18px;
                font-family: 'Segoe UI Semibold'; font-size: 13px;
            }
            QPushButton:hover { background-color: #00a381; }
            QPushButton:disabled {
                background-color: #b2d8d0; color: #ffffff;
            }
        """)
        self._btn_ok.clicked.connect(self._confirmar)

        btn_cerrar = QPushButton("Cancelar")
        btn_cerrar.setStyleSheet("""
            QPushButton {
                background-color: #dfe6e9; color: #2d3436;
                border-radius: 8px; padding: 8px 18px;
                font-family: 'Segoe UI Semibold'; font-size: 13px;
            }
            QPushButton:hover { background-color: #b2bec3; }
        """)
        btn_cerrar.clicked.connect(self.reject)

        footer = QHBoxLayout()
        footer.addStretch()
        footer.addWidget(btn_cerrar)
        footer.addWidget(self._btn_ok)
        root.addLayout(footer)

    #Carga y pintado del grid

    def _cargar_semana(self):
        viernes = self._lunes + timedelta(days=4)
        self._lbl_titulo.setText(
            f"Dr./Dra. {self._nombre_medico}  —  "
            f"{self._lunes.strftime('%d/%m/%Y')} – {viernes.strftime('%d/%m/%Y')}"
        )

        # Obtener datos del modelo
        citas = self._fn_citas(self._id_medico, self._lunes, viernes)
        bloqueados = self._fn_bloqueados(self._id_medico, self._lunes, viernes)

        # Conjunto rápido {(fecha_str, hora_str)}
        ocupadas = {(c['fecha'], c['hora']): c['paciente'] for c in citas}

        # Limpiar grid
        while self._grid.count():
            item = self._grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Cabecera de días (columnas 1..5, fila 0)
        self._grid.addWidget(QLabel(""), 0, 0)
        dias = [self._lunes + timedelta(days=i) for i in range(5)]
        for col, d in enumerate(dias, start=1):
            lbl = QLabel(f"{DIAS_ES[col-1]}\n{d.strftime('%d/%m')}")
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet(
                "font-family:'Segoe UI Semibold'; font-size:13px; color:#2d3436;"
                "background:#f8fafc; border:1px solid #dde3ea; border-radius:6px; padding:4px;"
            )
            self._grid.addWidget(lbl, 0, col)

        # Filas de franjas horarias
        for fila, franja in enumerate(FRANJAS, start=1):
            lbl_hora = QLabel(franja)
            lbl_hora.setAlignment(Qt.AlignCenter)
            lbl_hora.setFixedWidth(52)
            lbl_hora.setStyleSheet(
                "font-family:'Segoe UI'; font-size:12px; color:#636e72;"
            )
            self._grid.addWidget(lbl_hora, fila, 0)

            for col, d in enumerate(dias, start=1):
                fecha_str = str(d)
                bloqueado = fecha_str in bloqueados
                paciente  = ocupadas.get((fecha_str, franja))
                ocupada   = paciente is not None

                celda = self._crear_celda(d, franja, ocupada, bloqueado, paciente)
                self._grid.addWidget(celda, fila, col)

    def _crear_celda(self, fecha, hora, ocupada, bloqueado, paciente=None):
        btn = QPushButton()
        btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        btn.setMinimumHeight(36)

        # Comprobar si la franja horaria ya ha pasado
        pasada = False
        hoy = date.today()
        if not bloqueado and not ocupada:
            if fecha < hoy:
                # Día anterior: todas las franjas bloqueadas
                pasada = True
            elif fecha == hoy:
                # Hoy: solo las franjas cuya hora ya pasó
                h, m = int(hora.split(':')[0]), int(hora.split(':')[1])
                ahora = datetime.now()
                if (ahora.hour, ahora.minute) >= (h, m):
                    pasada = True

        if bloqueado or pasada:
            btn.setText("Bloqueado" if bloqueado else "Pasada")
            btn.setEnabled(False)
            color = COLOR_BLOQUEADA if bloqueado else COLOR_PASADA
            estilo_base = (f"background:{color}; color:#aaa;"
                           f"border:1px solid {BORDER_BLOQUEADA}; border-radius:6px;"
                           "font-size:11px; font-style: italic;")
            btn.setStyleSheet(estilo_base)
        elif ocupada:
            # Mostrar nombre del paciente truncado
            texto = paciente[:18] + "…" if len(paciente) > 18 else paciente
            btn.setText(texto)
            btn.setToolTip(f"Ocupada — {paciente}")
            btn.setEnabled(False)
            estilo_base = (f"background:{COLOR_OCUPADA}; color:#c0392b;"
                           f"border:1px solid {BORDER_OCUPADA}; border-radius:6px;"
                           "font-size:11px; font-family:'Segoe UI';")
            btn.setStyleSheet(estilo_base)
        else:
            btn.setText("Libre")
            btn.setToolTip(f"Haz clic para elegir {hora} el {fecha.strftime('%d/%m/%Y')}")
            estilo_base = (f"background:{COLOR_LIBRE}; color:#00a381;"
                           f"border:1px solid {BORDER_LIBRE}; border-radius:6px;"
                           "font-size:11px; font-family:'Segoe UI Semibold';")
            btn.setStyleSheet(estilo_base)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda _, f=fecha, h=hora, b=btn: self._elegir(f, h, b))

        return btn

    def _elegir(self, fecha, hora, boton):
        """Marca el botón elegido y habilita el botón Confirmar hora."""
        # Restaurar estilo del botón anteriormente seleccionado
        if self._btn_pendiente and self._btn_pendiente is not boton:
            self._btn_pendiente.setStyleSheet(
                f"background:{COLOR_LIBRE}; color:#00a381;"
                f"border:1px solid {BORDER_LIBRE}; border-radius:6px;"
                "font-size:11px; font-family:'Segoe UI Semibold';"
            )
            self._btn_pendiente.setText("Libre")

        # Marcar el nuevo botón como seleccionado
        boton.setStyleSheet(
            "background:#00b894; color:white;"
            "border:2px solid #00a381; border-radius:6px;"
            "font-size:12px; font-family:'Segoe UI Semibold';"
        )
        boton.setText("✓ Elegido")
        boton.setCursor(Qt.PointingHandCursor)

        self._hora_pendiente = (fecha, hora)
        self._btn_pendiente = boton
        self._btn_ok.setEnabled(True)

    def _confirmar(self):
        """Emite la señal con la hora elegida y cierra el diálogo."""
        if self._hora_pendiente:
            fecha, hora = self._hora_pendiente
            self.hora_seleccionada.emit(fecha, hora)
            self.accept()

    # ── Navegación semanal ────────────────────────────────────────────────────

    def _semana_anterior(self):
        self._lunes -= timedelta(days=7)
        self._cargar_semana()

    def _semana_siguiente(self):
        self._lunes += timedelta(days=7)
        self._cargar_semana()