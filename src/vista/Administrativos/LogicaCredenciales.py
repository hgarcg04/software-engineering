# Mixin de vista para CU5 (Generar Credenciales).
# VentanaAdministrativos hereda de esta clase.

from PyQt5.QtWidgets import QMessageBox


class LogicaCredenciales:

    def _init_credenciales(self):
        """Conecta señales y configura el estado inicial del formulario de credenciales."""
        self.btn_guardar_credencial.clicked.connect(self._guardar_credencial)
        self.btn_limpiar_credencial.clicked.connect(self._limpiar_credencial)
        self.combo_rol_personal.currentIndexChanged.connect(self._on_rol_cambiado)
        self.combo_especialidad_personal.setEnabled(False)  # Solo activo si rol = Médico

    # ── Callbacks ─────────────────────────────────────────────────────────────

    def _on_rol_cambiado(self):
        """Habilita el combo de especialidad solo cuando el rol seleccionado es Médico."""
        rol = self.combo_rol_personal.currentText()
        self.combo_especialidad_personal.setEnabled(rol == 'Médico')

    def _guardar_credencial(self):
        nombre       = self.input_nombre_personal.text().strip()
        apellidos    = self.input_apellidos_personal.text().strip()
        dni          = self.input_dni_personal.text().strip()
        rol          = self.combo_rol_personal.currentText()
        especialidad = self.combo_especialidad_personal.currentText()
        email        = self.input_email_personal.text().strip()

        exito, val1, val2 = self._controlador.generar_credenciales(
            nombre, apellidos, dni, rol, especialidad, email
        )

        if exito:
            # val1 = nombre_usuario, val2 = contraseña temporal
            QMessageBox.information(
                self, "Credenciales generadas",
                f"Empleado registrado correctamente.\n\n"
                f"Usuario: {val1}\n"
                f"Contraseña temporal: {val2}\n\n"
                "Comunica estas credenciales al empleado. "
                "Deberá cambiar la contraseña en su primer inicio de sesión."
            )
            self._limpiar_credencial()
        else:
            # val1 = mensaje de error
            QMessageBox.warning(self, "Error", val1)

    def _limpiar_credencial(self):
        self.input_nombre_personal.clear()
        self.input_apellidos_personal.clear()
        self.input_dni_personal.clear()
        self.input_email_personal.clear()
        self.combo_rol_personal.setCurrentIndex(0)
        self.combo_especialidad_personal.setCurrentIndex(0)
        self.combo_especialidad_personal.setEnabled(False)

    # ── Interfaz pública para el controlador ──────────────────────────────────

    def limpiar_formulario_credencial(self):
        """Permite al controlador limpiar el formulario si lo necesita."""
        self._limpiar_credencial()