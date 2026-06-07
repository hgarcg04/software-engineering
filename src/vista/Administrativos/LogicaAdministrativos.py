import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from PyQt5.QtWidgets import QMainWindow, QMessageBox
from PyQt5.QtCore import pyqtSignal, QTimer, QDateTime
from PyQt5 import uic

from src.vista.Administrativos.LogicaCitas import LogicaCitas
from src.vista.Administrativos.LogicaCredenciales import LogicaCredenciales
from src.vista.Administrativos.LogicaMedicamentos import LogicaMedicamentos
from src.vista.Administrativos.LogicaBackup import LogicaBackup
from src.vista.Administrativos.LogicaTablon import LogicaTablon

ui_path = os.path.join(os.path.dirname(__file__), "..", "Ui", "VistaAdministrativo.ui")

PAGE_INICIO       = 0
PAGE_PACIENTES    = 1
PAGE_CITAS        = 2
PAGE_AGENDA       = 3
PAGE_CREDENCIALES = 4
PAGE_MEDICAMENTOS = 5
PAGE_BACKUP       = 6

Form, Window = uic.loadUiType(ui_path)


class VentanaAdministrativos(QMainWindow, Form, LogicaCitas, LogicaCredenciales, LogicaMedicamentos, LogicaBackup, LogicaTablon):
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

        self.btn_logout.clicked.connect(self.cerrar_sesion)

        # Guardar / limpiar formulario de registro de paciente
        self.btn_guardar_paciente.clicked.connect(self.registrar_paciente)
        self.btn_limpiar_formulario.clicked.connect(self.limpiar_formulario_paciente)

        # Reloj en tiempo real
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._actualizar_fecha_hora)
        self.timer.start(1000)
        self._actualizar_fecha_hora()

        # Inicializar conexiones de Citas y Bloquear Agenda (mixin LogicaCitas)
        self._init_citas()

        # CU5: Generar Credenciales (mixin LogicaCredenciales)
        self._init_credenciales()

        # CU7: Pedir Medicamentos (mixin LogicaMedicamentos)
        self._init_medicamentos()

        # CU6: Copia de Seguridad (mixin LogicaBackup)
        self._init_backup()

        # Tablon de Tareas (mixin LogicaTablon)
        self._init_tablon()

    def cerrar_sesion(self):
        print("Cerrando sesión...")
        self.signal_logout.emit()
        self.close()

    def _navegar(self, indice):
        """
        Abre la pestaña indicada. Al entrar en cada sección inicializa sus datos.
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
        ]
        for i, btn in enumerate(nav_btns):
            btn.setChecked(i == indice)

        if indice == PAGE_PACIENTES and self._controlador:
            self._controlador.cargar_medicos_combo_paciente()

        if indice == PAGE_CITAS and self._controlador:
            self._controlador.inicializar_combos_cita()

        if indice == PAGE_AGENDA and self._controlador:
            self._controlador.cargar_todos_medicos()

        if indice == PAGE_MEDICAMENTOS and self._controlador:
            self._controlador.cargar_catalogo()

        if indice == PAGE_BACKUP and self._controlador:
            self._controlador.inicializar_backup()

        if indice == PAGE_INICIO and self._controlador:
            self._controlador.cargar_tareas()

    # ── Inicio: nombre de usuario y reloj ─────────────────────────────────────

    def cargar_datos_iniciales(self, userVO):
        """Llamado por el controlador al asignarse. Muestra el nombre del administrativo."""
        self.lbl_user_name.setText(f"Administrativo/a: {userVO.nombre} {userVO.apellidos}")

    def _actualizar_fecha_hora(self):
        """Actualiza lbl_datetime cada segundo."""
        self.lbl_datetime.setText(QDateTime.currentDateTime().toString("dd/MM/yyyy  HH:mm"))

    # ── Registrar Paciente ────────────────────────────────────────────────────

    def registrar_paciente(self):

        # ── Validación del combo de médico (es el único que no es texto) ─────
        id_medico = self.input_medico_paciente.currentData()
        if id_medico is None:
            QMessageBox.warning(self, "Campos obligatorios",
                                "Debes seleccionar un médico asignado.")
            return

        # ── Recogida de datos ─────────────────────────────────────────────────
        nif              = self.input_dni_paciente.text().strip().upper()
        nombre           = self.input_nombre_paciente.text().strip()
        ap1              = self.input_ap1_paciente.text().strip()
        ap2              = self.input_ap2_paciente.text().strip()
        email            = self.input_email_paciente.text().strip()
        telefono         = self.input_telefono_paciente.text().strip()
        direccion        = self.input_direccion_paciente.text().strip()
        alergias         = self.input_alergias_paciente.text().strip()
        fecha_nacimiento = self.input_fnac_paciente.date().toPyDate()
        genero           = self.input_genero_paciente.currentText()

        # ── Llamada al controlador ────────────────────────────────────────────
        if self._controlador:
            exito, mensaje = self._controlador.registrar_paciente(
                nif, nombre, ap1, ap2, fecha_nacimiento,
                genero, email, direccion, alergias, telefono,
                id_medico
            )
        else:
            return

        if exito:
            QMessageBox.information(self, "Éxito", mensaje)
            self.limpiar_formulario_paciente()
        else:
            QMessageBox.warning(self, "Error", mensaje)

    def limpiar_formulario_paciente(self):
        """Restablece todos los campos del formulario de registro de paciente."""
        from PyQt5.QtCore import QDate

        campos_texto = [
            self.input_dni_paciente,
            self.input_nombre_paciente,
            self.input_ap1_paciente,
            self.input_ap2_paciente,
            self.input_email_paciente,
            self.input_telefono_paciente,
            self.input_direccion_paciente,
            self.input_alergias_paciente,
        ]
        for campo in campos_texto:
            campo.clear()
            campo.setStyleSheet("")

        self.input_fnac_paciente.setDate(QDate.currentDate())
        self.input_genero_paciente.setCurrentIndex(0)
        self.input_medico_paciente.setCurrentIndex(0)  # resetea al placeholder

    # ── Métodos llamados por el controlador ───────────────────────────────────

    def cargar_combo_medico_paciente(self, medicos):
        """Puebla el combo de médico asignado con los datos recibidos del controlador."""
        self.input_medico_paciente.blockSignals(True)
        self.input_medico_paciente.clear()
        self.input_medico_paciente.addItem("— Selecciona un médico —", None)
        for m in medicos:
            # m = (id_empleado, nombre, apellidos, especialidad)
            self.input_medico_paciente.addItem(
                f"{m.apellidos}, {m.nombre}  [{m.especialidad}]", m.id_empleado
            )
        self.input_medico_paciente.blockSignals(False)

    # ── Property controlador ──────────────────────────────────────────────────

    @property
    def controlador(self):
        return self._controlador

    @controlador.setter
    def controlador(self, ref):
        self._controlador = ref