from src.modelo.VO.PacientesVO import PacientesVO
from datetime import date


class ControladorAdministrativos:
    def __init__(self, vista, modelo, user_vo):
        self._vista = vista
        self._modelo = modelo
        self.user_vo = user_vo

        # Estado interno de selección
        self._pacientes_busqueda = []
        self._medicos_busqueda_cache = []  # caché de médicos cargados en el combo
        self._paciente_cita = None
        self._medicos_busqueda = []
        self._medico_agenda_id = None

        # Cargar nombre y hora en la cabecera de la ventana
        self._vista.cargar_datos_iniciales(user_vo)

    def cerrar_sesion(self):
        self._vista.signal_logout.emit()

    # ── CU3: Registrar Paciente ───────────────────────────────────────────────

    def registrar_paciente(self, nif, nombre, apellido1, apellido2,
                           fecha_nacimiento, genero, correo,
                           direccion, alergias, telefono):
        # Validación: el DNI no puede estar ya registrado
        if self._modelo.existePaciente(nif):
            return False, "El paciente ya está registrado."

        pacienteVO = PacientesVO(
            nif=nif, nombre=nombre,
            apellido1=apellido1, apellido2=apellido2,
            fecha_nacimiento=fecha_nacimiento,
            genero=genero, correo=correo,
            direccion=direccion, alergias=alergias,
            telefono=telefono
        )
        self._modelo.registrarPaciente(pacienteVO)
        return True, "Paciente registrado correctamente."

    # ── CU4: Asignar Citas ────────────────────────────────────────────────────

    def inicializar_combos_cita(self):
        """Carga especialidades y médicos al entrar en la pestaña de Citas."""
        especialidades = self._modelo.obtenerEspecialidades()
        self._vista.cargar_especialidades(especialidades)
        self._filtrar_medicos_en_vista(None)

    def filtrar_medicos(self, especialidad):
        self._filtrar_medicos_en_vista(especialidad)

    def _filtrar_medicos_en_vista(self, especialidad):
        medicos = self._modelo.obtenerMedicosPorEspecialidad(especialidad)
        self._medicos_busqueda_cache = medicos  # caché para recuperar nombre en abrir_calendario
        self._vista.cargar_medicos(medicos)

    def limpiar_horas(self):
        self._vista.limpiar_horas()

    def buscar_paciente_cita(self, texto):
        """
        Busca pacientes. Si no hay resultados ofrece ir a registro (extensión CU4).
        """
        if not texto:
            self._vista.mostrar_error("Búsqueda vacía",
                                      "Introduce un NIF, nombre o apellido.")
            return

        resultados = self._modelo.buscarPaciente(texto)
        if not resultados:
            self._vista.redirigir_a_registro_paciente()
            return

        self._pacientes_busqueda = resultados
        self._vista.cargar_resultados_busqueda_paciente(resultados)

    def seleccionar_paciente(self, fila):
        if fila < len(self._pacientes_busqueda):
            self._paciente_cita = self._pacientes_busqueda[fila]
            self._vista.mostrar_paciente_seleccionado(self._paciente_cita.nombre_completo)

    def deseleccionar_paciente(self):
        self._paciente_cita = None
        self._vista.limpiar_seleccion_paciente()

    def abrir_calendario(self, id_medico):
        """Busca el nombre del médico seleccionado y abre el calendario semanal."""
        nombre_medico = ""
        for m in self._medicos_busqueda_cache:
            if m[0] == id_medico:
                nombre_medico = f"{m[2]}, {m[1]}"
                break
        self._vista.abrir_calendario_dialogo(id_medico, nombre_medico, self._modelo)

    def asignar_cita(self, id_medico, fecha, hora):
        if not self._paciente_cita:
            self._vista.mostrar_error("Sin paciente",
                                      "Selecciona primero un paciente de la tabla.")
            return
        if not id_medico:
            self._vista.mostrar_error("Sin médico", "Selecciona un médico.")
            return
        if not hora:
            self._vista.mostrar_error("Sin hora",
                                      "Consulta la disponibilidad y selecciona una hora.")
            return

        # Regla de negocio: paciente ingresado no puede recibir citas externas
        paciente = self._modelo.buscarPacientePorId(self._paciente_cita.id_paciente)
        if not paciente:
            self._vista.mostrar_error("Error", "Paciente no encontrado.")
            return
        if getattr(paciente[0], 'hospitalizado', None) in (1, True):
            self._vista.mostrar_error(
                "Paciente ingresado",
                "No se puede asignar una cita a un paciente actualmente ingresado."
            )
            return

        self._modelo.asignarCita(self._paciente_cita.id_paciente, id_medico, fecha, hora)
        self._paciente_cita = None
        self._vista.confirmar_cita_asignada()

    def limpiar_formulario_cita(self):
        """Resetea todos los campos de la pestaña de citas al estado inicial."""
        self._paciente_cita = None
        self._pacientes_busqueda = []
        self._vista._limpiar_todo_citas()

    # ── CU9: Bloquear Agenda ──────────────────────────────────────────────────

    def buscar_medico_agenda(self, texto):
        if not texto:
            self._vista.mostrar_error("Búsqueda vacía",
                                      "Introduce el nombre o apellidos del médico.")
            return

        resultados = self._modelo.buscarMedico(texto)
        if not resultados:
            self._vista.mostrar_info("Sin resultados",
                                     "No se encontró ningún médico con ese criterio.")
        self._medicos_busqueda = resultados
        self._vista.cargar_resultados_busqueda_medico(resultados)

    def seleccionar_medico_agenda(self, fila):
        if fila < len(self._medicos_busqueda):
            medico = self._medicos_busqueda[fila]
            self._medico_agenda_id = medico[0]
            self._vista.mostrar_medico_seleccionado(f"{medico[2]}, {medico[1]}")

    def bloquear_agenda(self, fecha_inicio, fecha_fin, motivo, observaciones):
        if not self._medico_agenda_id:
            self._vista.mostrar_error("Sin médico",
                                      "Selecciona primero un médico de la tabla.")
            return

        # Reglas de negocio CU9
        hoy = date.today()
        if fecha_inicio > fecha_fin:
            self._vista.mostrar_error("Fechas incorrectas",
                                      "La fecha de inicio es posterior a la fecha de fin.")
            return
        if fecha_inicio <= hoy or fecha_fin <= hoy:
            self._vista.mostrar_error("Fechas incorrectas",
                                      "Solo se pueden bloquear fechas futuras.")
            return
        if (fecha_fin - fecha_inicio).days + 1 > 15:
            self._vista.mostrar_error("Rango excesivo",
                                      "Solo se permite bloquear un máximo de 15 días consecutivos.")
            return
        if self._modelo.hayCitasEnRango(self._medico_agenda_id, fecha_inicio, fecha_fin):
            self._vista.mostrar_error("Agenda ocupada",
                                      "Ya hay consultas asignadas en las fechas solicitadas.")
            return

        self._modelo.bloquearAgenda(
            self._medico_agenda_id, fecha_inicio, fecha_fin, motivo, observaciones
        )
        self._medico_agenda_id = None
        self._vista.confirmar_agenda_bloqueada()