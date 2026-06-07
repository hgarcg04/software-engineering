from src.modelo.VO.PacientesVO import PacientesVO
from src.modelo.SingletonLog import SingletonLog
from datetime import date, datetime
import secrets
import string
import re

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
        self._pedido_en_curso = {}  # {id_medicamento: (nombre, cantidad, unidad)}

        # Cargar nombre y hora en la cabecera de la ventana
        self._vista.cargar_datos_iniciales(user_vo)

    def cerrar_sesion(self):
        self._vista.signal_logout.emit()

    # ── CU3: Registrar Paciente ───────────────────────────────────────────────

    def registrar_paciente(self, nif, nombre, apellido1, apellido2,
                           fecha_nacimiento, genero, correo,
                           direccion, alergias, telefono):

        # ── Validaciones de formato ───────────────────────────────────────────
        nif_limpio = nif.strip().upper()
        if not re.fullmatch(r'[0-9]{8}[A-Z]', nif_limpio):
            return False, "El NIF no tiene un formato válido (8 dígitos + letra, ej: 12345678A)."

        if fecha_nacimiento >= date.today():
            return False, "La fecha de nacimiento no puede ser hoy ni una fecha futura."

        if not re.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+', correo):
            return False, "El correo electrónico no tiene un formato válido."

        if not re.fullmatch(r'[0-9\s\+\-]{7,15}', telefono):
            return False, "El teléfono no tiene un formato válido."

        # ── Validación de duplicado ───────────────────────────────────────────
        if self._modelo.existePaciente(nif_limpio):
            return False, "Ya existe un paciente registrado con ese NIF."

        # ── Persistencia ─────────────────────────────────────────────────────
        pacienteVO = PacientesVO(
            nif=nif_limpio, nombre=nombre,
            apellido1=apellido1, apellido2=apellido2,
            fecha_nacimiento=fecha_nacimiento,
            genero=genero, correo=correo,
            direccion=direccion, alergias=alergias,
            telefono=telefono
        )
        self._modelo.registrarPaciente(pacienteVO)
        return True, f"Paciente {nombre} {apellido1} registrado correctamente."

    # ── CU4: Asignar Citas ────────────────────────────────────────────────────

    def inicializar_combos_cita(self):
        """Carga especialidades, médicos y todos los pacientes al entrar en Citas."""
        especialidades = self._modelo.obtenerEspecialidades()
        self._vista.cargar_especialidades(especialidades)
        self._filtrar_medicos_en_vista(None)
        self.cargar_todos_pacientes()

    def filtrar_medicos(self, especialidad):
        self._filtrar_medicos_en_vista(especialidad)

    def _filtrar_medicos_en_vista(self, especialidad):
        medicos = self._modelo.obtenerMedicosPorEspecialidad(especialidad)
        self._medicos_busqueda_cache = medicos  # caché para recuperar nombre en abrir_calendario
        self._vista.cargar_medicos(medicos)

    def limpiar_horas(self):
        self._vista.limpiar_horas()

    def cargar_todos_pacientes(self):
        """Carga todos los pacientes al entrar en la pestaña de Citas."""
        todos = self._modelo.buscarPaciente("")
        self._pacientes_busqueda = todos
        self._vista.cargar_resultados_busqueda_paciente(todos)
        self._vista.mostrar_btn_no_encontrado(False)

    def filtrar_pacientes(self, texto):
        """
        Filtra la lista de pacientes localmente a medida que el usuario escribe.
        Si no hay resultados muestra el botón de paciente no encontrado.
        """
        if not texto.strip():
            # Sin texto: mostrar todos
            self._vista.cargar_resultados_busqueda_paciente(self._pacientes_busqueda)
            self._vista.mostrar_btn_no_encontrado(False)
            return

        texto_lower = texto.lower()
        filtrados = [
            p for p in self._pacientes_busqueda
            if texto_lower in p.nif.lower()
            or texto_lower in p.nombre.lower()
            or texto_lower in (p.apellido1 or "").lower()
            or texto_lower in (p.apellido2 or "").lower()
        ]

        self._vista.cargar_resultados_busqueda_paciente(filtrados)
        # Mostrar botón no encontrado solo si la búsqueda activa no da resultados
        self._vista.mostrar_btn_no_encontrado(len(filtrados) == 0)

    def seleccionar_paciente(self, fila):
        if fila < len(self._pacientes_busqueda):
            self._paciente_cita = self._pacientes_busqueda[fila]
            self._vista.mostrar_paciente_seleccionado(self._paciente_cita.nombre_completo)

    def deseleccionar_paciente(self):
        self._paciente_cita = None
        self._vista.limpiar_seleccion_paciente()
        self.cargar_todos_pacientes()

    def ir_a_registro_paciente(self):
        """Redirige a la pestaña de registro cuando el paciente no existe."""
        self._vista.navegar_a_registro()

    def abrir_calendario(self, id_medico, fecha=None):
        """Busca el nombre del médico seleccionado y abre el calendario semanal."""
        nombre_medico = ""
        for m in self._medicos_busqueda_cache:
            if m[0] == id_medico:
                nombre_medico = f"{m[2]}, {m[1]}"
                break
        self._vista.abrir_calendario_dialogo(id_medico, nombre_medico, self._modelo, fecha_inicial=fecha)

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

        # ── Notificación por email (CU4) ──────────────────────────────────────
        # Los datos del paciente y del médico ya están en memoria; no hace falta
        # ninguna consulta adicional ni lógica nueva en Logica.
        try:
            nombre_medico = ""
            for m in self._medicos_busqueda_cache:
                if m[0] == id_medico:
                    nombre_medico = f"{m[1]} {m[2]}"
                    break
            self._modelo.enviarConfirmacionCita(
                correo_paciente = self._paciente_cita.correo,
                nombre_paciente = self._paciente_cita.nombre_completo,
                nombre_medico   = nombre_medico,
                fecha           = str(fecha),
                hora            = str(hora),
            )
        except Exception as e:
            # El fallo de email NO revierte la cita ya persistida en BD
            print(f"ControladorAdministrativos: no se pudo enviar la confirmación: {e}")
        # ─────────────────────────────────────────────────────────────────────

        self._paciente_cita = None
        self._vista.confirmar_cita_asignada()
        self.cargar_todos_pacientes()

    def limpiar_formulario_cita(self):
        """Resetea todos los campos de la pestaña de citas al estado inicial."""
        self._paciente_cita = None
        self._vista.limpiar_formulario_cita()
        self.cargar_todos_pacientes()

    # ── CU9: Bloquear Agenda ──────────────────────────────────────────────────

    def cargar_todos_medicos(self):
        """Carga todos los médicos al entrar en la pestaña de Bloquear Agenda."""
        todos = self._modelo.buscarMedico("")
        self._medicos_busqueda = todos
        self._vista.cargar_resultados_busqueda_medico(todos)

    def filtrar_medicos_agenda(self, texto):
        """Filtra localmente la lista de médicos a medida que el usuario escribe."""
        if not texto.strip():
            self._vista.cargar_resultados_busqueda_medico(self._medicos_busqueda)
            return
        texto_lower = texto.lower()
        filtrados = [
            m for m in self._medicos_busqueda
            if texto_lower in m[1].lower()          # nombre
            or texto_lower in m[2].lower()          # apellidos
            or texto_lower in (m[3] or "").lower()  # especialidad
        ]
        self._vista.cargar_resultados_busqueda_medico(filtrados)

    def buscar_medico_agenda(self, texto):
        """Búsqueda explícita (botón Buscar). Actualiza la caché y la tabla."""
        resultados = self._modelo.buscarMedico(texto)
        if not resultados and texto:
            self._vista.mostrar_info("Sin resultados",
                                     "No se encontró ningún médico con ese criterio.")
        self._medicos_busqueda = resultados
        self._vista.cargar_resultados_busqueda_medico(resultados)

    def seleccionar_medico_agenda(self, fila):
        if fila < len(self._medicos_busqueda):
            medico = self._medicos_busqueda[fila]
            self._medico_agenda_id = medico[0]
            self._vista.mostrar_medico_seleccionado(f"{medico[2]}, {medico[1]}")

    def deseleccionar_medico_agenda(self):
        """Limpia la selección de médico sin borrar la tabla ni el buscador."""
        self._medico_agenda_id = None
        self._vista.limpiar_seleccion_medico()

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
        if fecha_inicio <= hoy:
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

        exito, msg = self._modelo.bloquearAgenda(
            self._medico_agenda_id, fecha_inicio, fecha_fin, motivo, observaciones
        )
        if exito:
            self._medico_agenda_id = None
            self._vista.confirmar_agenda_bloqueada()
        else:
            self._vista.mostrar_error("Error en base de datos", msg)
    # ── CU5: Generar Credenciales ─────────────────────────────────────────────

    def generar_credenciales(self, nombre, apellidos, dni, rol, especialidad, email):
        # Validacion: campos obligatorios
        if not nombre.strip() or not apellidos.strip():
            return False, "El nombre y los apellidos son obligatorios.", None
        if not dni.strip():
            return False, "El DNI es obligatorio.", None
        if rol == '-- Seleccionar rol --':
            return False, "Debes seleccionar un rol.", None
        if not email.strip():
            return False, "El correo electrónico es obligatorio.", None

        # Validacion: el DNI no puede estar ya registrado (flujo alternativo CU5)
        if self._modelo.existeEmpleado(dni):
            return False, "Ya existe un empleado registrado con ese DNI.", None

        # Mapeo rol legible -> valor BD
        mapa_roles = {
            'Médico': 'medico',
            'Enfermero/a': 'enfermero',
            'Administrativo/a': 'administrativo',
        }
        rol_bd = mapa_roles.get(rol, rol.lower())

        # Especialidad solo aplica a medicos
        esp = especialidad if rol_bd == 'medico' and especialidad != '-- No aplica --' else None

        # Generar nombre de usuario: primera letra nombre + apellidos sin espacios, minusculas
        nombre_usuario = (nombre[0] + apellidos.replace(' ', '')).lower()

        # Generar password aleatoria: 10 caracteres (letras + digitos)
        alfabeto = string.ascii_letters + string.digits
        password_generada = ''.join(secrets.choice(alfabeto) for _ in range(10))

        exito, val1, val2 = self._modelo.generarCredenciales(
            dni, nombre, apellidos, nombre_usuario,
            password_generada, email, rol_bd, esp
        )

        if exito:
            return True, nombre_usuario, password_generada
        else:
            return False, val1, None  # val1 contiene el mensaje de error

    def limpiar_formulario_credencial(self):
        self._vista.limpiar_formulario_credencial()
    # ── CU7: Pedir Medicamentos ───────────────────────────────────────────────

    def cargar_catalogo(self):
        """
        Obtiene el listado completo de medicamentos del modelo y lo envía a la vista.
        Se llama desde _navegar() al entrar en PAGE_MEDICAMENTOS.
        """
        medicamentos = self._modelo.obtenerMedicamentos()
        self._vista.cargar_catalogo_medicamentos(medicamentos)

    def confirmar_pedido(self, pedido):
        """
        Recibe el diccionario {id_medicamento: (nombre, cantidad, unidad)} desde la vista,
        valida que haya al menos una línea con cantidad > 0, actualiza el stock de cada
        medicamento y notifica a la vista si todo fue bien.

        Parámetros
        ----------
        pedido : dict
            {id_medicamento (int): (nombre (str), cantidad (int), unidad (str))}
        """
        # Precondición: al menos una línea
        if not pedido:
            self._vista.mostrar_error("Pedido vacío",
                                      "Añade al menos un medicamento antes de confirmar.")
            return

        # Validar que todas las cantidades sean positivas
        for id_med, (nombre, cantidad, _) in pedido.items():
            if cantidad <= 0:
                self._vista.mostrar_error(
                    "Cantidad inválida",
                    f"La cantidad de «{nombre}» debe ser mayor que cero."
                )
                return

        # Persistencia: actualizar stock de cada línea (reabastecimiento → suma)
        for id_med, (_, cantidad, _) in pedido.items():
            self._modelo.actualizarStock(id_med, cantidad)

        # Actualizar alertas: si tras el pedido el stock ya supera el mínimo, desactivar alerta
        medicamentos_actualizados = self._modelo.obtenerMedicamentos()
        for med in medicamentos_actualizados:
            if med.alerta_stock and med.stock > med.stock_minimo:
                self._modelo.setAlertaStock(med.id_medicamento, 0)

        # Notificar éxito a la vista
        self._vista.confirmar_pedido_exitoso()

        # Recargar el catálogo con los stocks actualizados
        self.cargar_catalogo()
    # ── CU6: Copia de Seguridad ───────────────────────────────────────────────

    def inicializar_backup(self):
        """Carga el historial al entrar en la pestaña de backup."""
        historial = self._modelo.obtenerHistorialBackup()
        self._vista.cargar_historial_backup(historial)
        if historial:
            f = historial[0]
            self._vista.actualizar_ultima_copia(f[0], f[1], f[4], f[3])

    def crear_backup(self, ruta_destino, tipo):
        # Flujo alternativo 2a: comprobar espacio antes de empezar
        hay_espacio, libre_kb, necesario_kb = self._modelo.comprobarEspacioBackup(ruta_destino)
        if not hay_espacio:
            self._vista.mostrar_error(
                "Espacio insuficiente",
                f"Espacio libre: {libre_kb:,} KB — Espacio estimado necesario: {necesario_kb:,} KB.\n"
                "Libera espacio o selecciona otra unidad."
            )
            return

        # Mostrar progreso e iniciar la copia
        self._vista.mostrar_progreso_backup(True)
        self._vista.habilitar_btn_backup(False)

        try:
            exito, mensaje, tamanio_kb = self._modelo.realizarBackup(
                ruta_destino, tipo, self.user_vo
            )
        except Exception as e:
            self._vista.finalizar_progreso_backup()
            self._vista.habilitar_btn_backup(True)
            self._vista.mostrar_error("Error inesperado", str(e))
            return

        self._vista.finalizar_progreso_backup()
        self._vista.habilitar_btn_backup(True)

        if exito:
            # Registrar en log de actividad
            SingletonLog().registrar_backup(self.user_vo, tipo, tamanio_kb)
            # Actualizar vista
            ahora = datetime.now()
            self._vista.actualizar_ultima_copia(
                ahora.strftime('%Y-%m-%d'),
                ahora.strftime('%H:%M:%S'),
                f"{self.user_vo.nombre} {self.user_vo.apellidos}",
                tamanio_kb
            )
            historial = self._modelo.obtenerHistorialBackup()
            self._vista.cargar_historial_backup(historial)
            self._vista.mostrar_info("Copia completada", mensaje)
        else:
            self._vista.mostrar_error("Error en la copia", mensaje)

    # ── Tablón de Tareas ──────────────────────────────────────────────────────

    def cargar_tareas(self):
        tareas = self._modelo.obtenerTareas()
        self._vista.cargar_tareas(tareas)

    def marcar_tarea_hecha(self, id_tarea):
        exito = self._modelo.eliminarTarea(id_tarea)
        if exito:
            self._vista.confirmar_tarea_eliminada()
        else:
            self._vista.mostrar_error("Error", "No se pudo eliminar la tarea. Inténtalo de nuevo.")