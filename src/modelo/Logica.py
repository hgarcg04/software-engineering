from src.modelo.dao.UserDaoJDBC import UserDaoJDBC
from src.modelo.dao.ConstanteDaoJDBC import ConstanteDaoJDBC
from src.modelo.dao.TratamientosDaoJDBC import TratamientosDaoJDBC
from src.modelo.dao.TomasDaoJDBC import TomasDaoJDBC
from src.modelo.dao.CitasDaoJDBC import CitasDaoJDBC
from src.modelo.dao.PacientesDaoJDBC import PacientesDaoJDBC
from src.modelo.dao.MedicamentosDaoJDBC import MedicamentosDaoJDBC
from src.modelo.dao.EpisodiosDaoJDBC import EpisodiosDaoJDBC





class Logica():
    
    def comprobarLogin(self, loginVO):
        login_dao = UserDaoJDBC()
        return login_dao.consultarLogin(loginVO)
    
    def obtenerPacientes(self, UserVO):
        paciente_dao = PacientesDaoJDBC()
        return paciente_dao.devuelve_pacientes_ingresados(UserVO)
    
    def guardarConstante(self, constanteVO):
        constante_dao = ConstanteDaoJDBC()
        constante_dao.guardar_constante(constanteVO)
    
    def consultarHistoricoConstantes(self, id_episodio, tipo, desde, hasta):
        constante_dao = ConstanteDaoJDBC()
        return constante_dao.consultar_historico(id_episodio, tipo, desde, hasta)
    
    def obtenerTratamientos(self, pacienteVO):
        tratamiento_dao = TratamientosDaoJDBC()
        return tratamiento_dao.devuelve_tratamientos(pacienteVO)

    def guardarNuevaToma(self, tomaVO):
        toma_dao = TomasDaoJDBC()
        toma_dao.guardar_nueva_toma(tomaVO)
    
    def obtenerUltimaToma(self, tratamientoVO):
        toma_dao = TomasDaoJDBC()
        return toma_dao.obtener_ultima_toma(tratamientoVO)
     
    def obtenerTomasSesionActual(self, pacienteVO):
        toma_dao = TomasDaoJDBC()
        return toma_dao.obtener_tomas_sesion_actual(pacienteVO)
    
    def obtenerAgendaHoy(self, userVO):
        dao = CitasDaoJDBC()
        return dao.obtener_agenda_hoy(userVO)

    def obtenerAgenda(self, userVO, desde, hasta):
        dao = CitasDaoJDBC()
        return dao.obtener_agenda(userVO, desde, hasta)

    def guardarEpisodio(self, episodioVO):
        dao = EpisodiosDaoJDBC()
        dao.guardar_episodio(episodioVO)

    def ingresarPaciente(self, id_paciente, id_medico):
        dao = PacientesDaoJDBC()
        dao.ingresar_paciente(id_paciente, id_medico)

    def guardarTratamiento(self, tratamientoVO):
        dao = TratamientosDaoJDBC()
        dao.guardar_tratamiento(tratamientoVO)

    def buscarPaciente(self, texto):
        dao = PacientesDaoJDBC()
        return dao.buscar_paciente(texto)

    def obtenerEpisodios(self, id_paciente):
        dao = EpisodiosDaoJDBC()
        return dao.obtener_episodios(id_paciente)
    
    def guardarConsultaEnEpisodio(self, id_episodio, diagnostico, sintomas=None):
        dao = EpisodiosDaoJDBC()
        dao.guardar_consulta_en_episodio(id_episodio, diagnostico, sintomas)
    
    def obtenerTratamientos_por_episodio(self, id_episodio):
        dao = TratamientosDaoJDBC()
        return dao.obtener_tratamientos_por_episodio(id_episodio)
    
    def obtenerMedicamentos(self):
        dao = MedicamentosDaoJDBC()
        return dao.obtener_medicamentos()
    
    def buscarPacientePorId(self, id_paciente):
        dao = PacientesDaoJDBC()
        return dao.buscar_paciente_por_id(id_paciente)

    def actualizarStock(self, id_medicamento, cantidad):
        dao = MedicamentosDaoJDBC()
        dao.actualizar_stock(id_medicamento, cantidad)

    def registrarPaciente(self, pacienteVO):
        dao = PacientesDaoJDBC()
        dao.registrar_paciente(pacienteVO)

    def existePaciente(self, nif):
        dao = PacientesDaoJDBC()
        return dao.existe_paciente(nif)

    # --- CU4: Asignar Citas ---

    def obtenerEspecialidades(self):
        # Devuelve las especialidades disponibles para el combo de la vista
        dao = CitasDaoJDBC()
        return dao.obtener_especialidades()

    def obtenerMedicosPorEspecialidad(self, especialidad=None):
        # Devuelve los médicos filtrados por especialidad (None = todos)
        dao = CitasDaoJDBC()
        return dao.obtener_medicos_por_especialidad(especialidad)

    def consultarDisponibilidad(self, id_medico, fecha):
        # Devuelve horas libres del médico en esa fecha, o None si el día está bloqueado
        dao = CitasDaoJDBC()
        return dao.consultar_disponibilidad(id_medico, fecha)

    def obtenerCitasSemana(self, id_medico, fecha_inicio, fecha_fin):
        # Devuelve lista de dicts {fecha, hora, paciente, motivo} para el calendario
        dao = CitasDaoJDBC()
        return dao.obtener_citas_semana(id_medico, fecha_inicio, fecha_fin)

    def obtenerDiasBloqueadosSemana(self, id_medico, fecha_inicio, fecha_fin):
        # Devuelve conjunto de fechas bloqueadas en el rango para el calendario
        dao = CitasDaoJDBC()
        return dao.obtener_dias_bloqueados_semana(id_medico, fecha_inicio, fecha_fin)

    def asignarCita(self, id_paciente, id_medico, fecha, hora):
        dao = CitasDaoJDBC()
        dao.asignar_cita(id_paciente, id_medico, fecha, hora)

    # --- CU9: Bloquear Agenda ---

    def buscarMedico(self, texto):
        # Búsqueda de médicos por nombre o apellidos
        dao = CitasDaoJDBC()
        return dao.buscar_medico(texto)

    def bloquearAgenda(self, id_medico, fecha_inicio, fecha_fin, motivo, observaciones):
        dao = CitasDaoJDBC()
        dao.bloquear_agenda(id_medico, fecha_inicio, fecha_fin, motivo, observaciones)

    def hayCitasEnRango(self, id_medico, fecha_inicio, fecha_fin):
        # Expone la consulta al DAO para que el controlador pueda validar
        dao = CitasDaoJDBC()
        return dao.hay_citas_en_rango(id_medico, fecha_inicio, fecha_fin)