import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                              QLabel, QPushButton, QFileDialog, QFrame)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from src.modelo.LogicaNeumonia import LogicaNeumonia
from src.controlador.ControladorNeumonia import ControladorNeumonia


class VentanaNeumonia(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KURA - Clasificación de Neumonía")
        self._ruta_imagen = None
        self._modelo_ia = LogicaNeumonia()
        self._init_ui()
        self._controlador = ControladorNeumonia(self, self._modelo_ia)

    def _init_ui(self):
        self.setStyleSheet("QMainWindow { background-color: #a2bdf2; }")

        central = QWidget()
        self.setCentralWidget(central)
        layout_principal = QVBoxLayout(central)
        layout_principal.setContentsMargins(60, 60, 60, 60)
        layout_principal.setSpacing(20)

        # Título
        self.lbl_titulo = QLabel("Clasificación de Neumonía")
        self.lbl_titulo.setStyleSheet("font-family: 'Segoe UI Black'; font-size: 28px; color: #2d3436;")
        layout_principal.addWidget(self.lbl_titulo)

        self.lbl_sub = QLabel("Sube una radiografía de tórax para analizarla.")
        self.lbl_sub.setStyleSheet("font-family: 'Segoe UI'; font-size: 14px; color: #636e72;")
        layout_principal.addWidget(self.lbl_sub)

        # Área de imagen
        self.lbl_imagen = QLabel("No hay imagen seleccionada")
        self.lbl_imagen.setAlignment(Qt.AlignCenter)
        self.lbl_imagen.setMinimumSize(400, 350)
        self.lbl_imagen.setStyleSheet("""
            background-color: white;
            border-radius: 16px;
            color: #b2bec3;
            font-family: 'Segoe UI';
            font-size: 14px;
        """)
        layout_principal.addWidget(self.lbl_imagen)

        # Botones
        layout_botones = QHBoxLayout()

        self.btn_subir = QPushButton("Seleccionar imagen")
        self.btn_subir.setStyleSheet("""
            QPushButton { background-color: #6a9edb; color: white; border-radius: 12px;
                          padding: 10px 24px; font-family: 'Segoe UI Semibold'; font-size: 14px; }
            QPushButton:hover { background-color: #5a8dc7; }
        """)
        self.btn_subir.clicked.connect(self._seleccionar_imagen)

        self.btn_analizar = QPushButton("Analizar")
        self.btn_analizar.setEnabled(False)
        self.btn_analizar.setStyleSheet("""
            QPushButton { background-color: #00b894; color: white; border-radius: 12px;
                          padding: 10px 24px; font-family: 'Segoe UI Semibold'; font-size: 14px; }
            QPushButton:hover { background-color: #00a381; }
            QPushButton:disabled { background-color: #b2d8d0; }
        """)
        self.btn_analizar.clicked.connect(self._analizar)

        layout_botones.addWidget(self.btn_subir)
        layout_botones.addWidget(self.btn_analizar)
        layout_botones.addStretch()
        layout_principal.addLayout(layout_botones)

        # Resultado
        self.frame_resultado = QFrame()
        self.frame_resultado.setVisible(False)
        self.frame_resultado.setStyleSheet("background-color: white; border-radius: 16px; padding: 20px;")
        layout_resultado = QVBoxLayout(self.frame_resultado)

        self.lbl_resultado = QLabel()
        self.lbl_resultado.setStyleSheet("font-family: 'Segoe UI Black'; font-size: 22px;")
        self.lbl_resultado.setAlignment(Qt.AlignCenter)

        self.lbl_confianza = QLabel()
        self.lbl_confianza.setStyleSheet("font-family: 'Segoe UI'; font-size: 14px; color: #636e72;")
        self.lbl_confianza.setAlignment(Qt.AlignCenter)

        layout_resultado.addWidget(self.lbl_resultado)
        layout_resultado.addWidget(self.lbl_confianza)
        layout_principal.addWidget(self.frame_resultado)

    def _seleccionar_imagen(self):
        ruta, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar radiografía", "",
            "Imágenes (*.png *.jpg *.jpeg)"
        )
        if ruta:
            self._ruta_imagen = ruta
            pixmap = QPixmap(ruta).scaled(400, 350, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.lbl_imagen.setPixmap(pixmap)
            self.btn_analizar.setEnabled(True)
            self.frame_resultado.setVisible(False)

    def _analizar(self):
        if self._ruta_imagen:
            self.btn_analizar.setEnabled(False)
            self.btn_analizar.setText("Analizando...")
            self._controlador.clasificar_imagen(self._ruta_imagen)
            self.btn_analizar.setEnabled(True)
            self.btn_analizar.setText("Analizar")

    def mostrar_resultado(self, label, confianza):
        self.frame_resultado.setVisible(True)
        if label == "PNEUMONIA":
            self.lbl_resultado.setText("⚠ NEUMONÍA DETECTADA")
            self.lbl_resultado.setStyleSheet("font-family: 'Segoe UI Black'; font-size: 22px; color: #e17055;")
        else:
            self.lbl_resultado.setText("✔ NORMAL")
            self.lbl_resultado.setStyleSheet("font-family: 'Segoe UI Black'; font-size: 22px; color: #00b894;")
        self.lbl_confianza.setText(f"Confianza: {confianza}%")

    def mostrar_error(self, mensaje):
        self.frame_resultado.setVisible(True)
        self.lbl_resultado.setText("Error al analizar la imagen")
        self.lbl_resultado.setStyleSheet("font-family: 'Segoe UI Black'; font-size: 18px; color: #e17055;")
        self.lbl_confianza.setText(mensaje)