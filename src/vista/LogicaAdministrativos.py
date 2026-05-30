import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from PyQt5.QtWidgets import QMainWindow, QMessageBox
from PyQt5.QtCore import pyqtSignal, QTimer, QDateTime
from PyQt5 import uic

from src.vista.LogicaCitas import LogicaCitas
from src.vista.LogicaCredenciales import LogicaCredenciales

ui_path = os.path.join(os.path.dirname(__file__), "Ui/VistaAdministrativo.ui")

PAGE_INICIO       = 0
PAGE_PACIENTES    = 1
PAGE_CITAS        = 2
PAGE_AGENDA       = 3
PAGE_CREDENCIALES = 4
PAGE_MEDICAMENTOS = 5
PAGE_BACKUP       = 6
PAGE_PASSWORD     = 7



Form, Window = uic.loadUiType(ui_path)


class VentanaAdministrativos(QMainWindow, Form, LogicaCitas, LogicaCredenciales):
    signal_logout = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self._controlador = None

        # Navegación entre páginas
        self.btn_nav_inicio.clicked.connect(lambda: self._navegar(PAGE_INICIO))
        self.btn_nav_pacientes.clicked.connect(lambda: self._navegar(PAGE_PACIENTES))
        self.btn_nav_citas.clicked.connect(lambda: self._navegar(PAGE_CITAS))
        self.btn_nav_agenda.clicked.connect(lambda: self._navegar(PAGE_AGENDA))
        self.btn_nav_credenciales.clicked.connect(lambda: self._navegar(PAGE_CREDENCIALES))
        self.btn_nav_medicamentos.clicked.connect(lambda: self._navegar(PAGE_MEDICAMENTOS))
        self.btn_nav_backup.clicked.connect(lambda: self._navegar(PAGE_BACKUP))

        self.btn_nav_password.clicked.connect(self._ir_password)

        self.btn_logout.clicked.connect(self.cerrar_sesion)

        # Guardar paciente registrado
        self.btn_guardar_paciente.clicked.connect(self.registrar_paciente)

        # Reloj en tiempo real
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._actualizar_fecha_hora)
        self.timer.start(1000)
        self._actualizar_fecha_hora()

        # Inicializar conexiones de Citas y Bloquear Agenda (mixin LogicaCitas)
        self._init_citas()

        # CU5: Generar Credenciales (mixin LogicaCredenciales)
        self._init_credenciales()

        # --- Cambio contraseña -----
        self.btn_pw_confirmar.clicked.connect(self._cambiar_password)

    def cerrar_sesion(self):
        print("Cerrando sesión...")
        self.signal_logout.emit()
        self.close()

    def _navegar(self, indice):
        """
        Abre la pestaña indicada. Al entrar en Citas inicializa los combos.
        """
        self.stackedWidget.setCurrentIndex(indice)
        nav_btns = [
            self.btn_nav_inicio,
            self.btn_nav_pacientes,
            self.btn_nav_citas,
            self.btn_nav_agenda,
            self.btn_nav_credenciales,
            self.btn_nav_medicamentos,
            self.btn_nav_backup,
            self.btn_nav_password,
        ]
        for i, btn in enumerate(nav_btns):
            btn.setChecked(i == indice)

        if indice == PAGE_CITAS and self._controlador:
            self._controlador.inicializar_combos_cita()

        if indice == PAGE_AGENDA and self._controlador:
            self._controlador.cargar_todos_medicos()

    # ── Inicio: nombre de usuario y reloj ─────────────────────────────────────

    def cargar_datos_iniciales(self, userVO):
        """Llamado por el controlador al asignarse. Muestra el nombre del administrativo."""
        self.lbl_user_name.setText(f"Administrativo/a: {userVO.nombre} {userVO.apellidos}")

    def _actualizar_fecha_hora(self):
        """Actualiza lbl_datetime cada segundo."""
        self.lbl_datetime.setText(QDateTime.currentDateTime().toString("dd/MM/yyyy  HH:mm"))

    # ── Registrar Paciente ────────────────────────────────────────────────────

    def registrar_paciente(self):
        nif             = self.input_dni_paciente.text()
        nombre          = self.input_nombre_paciente.text()
        ap1             = self.input_ap1_paciente.text()
        ap2             = self.input_ap2_paciente.text()
        email           = self.input_email_paciente.text()
        telefono        = self.input_telefono_paciente.text()
        direccion       = self.input_direccion_paciente.text()
        alergias        = self.input_alergias_paciente.text()
        fecha_nacimiento = self.input_fnac_paciente.date().toPyDate()
        genero          = self.input_genero_paciente.currentText()

        exito, mensaje = self.controlador.registrar_paciente(
            nif, nombre, ap1, ap2, fecha_nacimiento,
            genero, email, direccion, alergias, telefono
        )

        if exito:
            QMessageBox.information(self, "Éxito", mensaje)
        else:
            QMessageBox.warning(self, "Error", mensaje)


    # ---------------------------------------------------------------------------------------------------------------------------------------------------------------
    #                                                                            CAMBIAR CONTRASEÑA
    # --------------------------------------------------------------------------------------------------------------------------------------------------------------

    def _ir_password(self):
        self._navegar(PAGE_PASSWORD)
        self.input_pw_nueva.clear()
        self.input_pw_confirmar.clear()
        self.lbl_pw_error_coincidencia.setVisible(False)
        self.lbl_pw_error_igual.setVisible(False)
        self.lbl_pw_ok.setVisible(False)

    def _cambiar_password(self):
        nueva = self.input_pw_nueva.text().strip()
        confirmar = self.input_pw_confirmar.text().strip()

        # Ocultar todos los mensajes
        self.lbl_pw_error_coincidencia.setVisible(False)
        self.lbl_pw_error_igual.setVisible(False)
        self.lbl_pw_ok.setVisible(False)

        if nueva != confirmar:
            self.lbl_pw_error_coincidencia.setVisible(True)
            self.input_pw_nueva.clear()
            self.input_pw_confirmar.clear()
            return


        self.controlador.cambiar_password(nueva, self.userVO)
        print("Boton de cambar contraseña presionado")
        self.lbl_pw_ok.setVisible(True)
        self.input_pw_nueva.clear()
        self.input_pw_confirmar.clear()




    # ── Property controlador ──────────────────────────────────────────────────

    @property
    def controlador(self):
        return self._controlador

    @controlador.setter
    def controlador(self, ref):
        self._controlador = ref