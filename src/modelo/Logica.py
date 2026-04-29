from src.modelo.dao.UserDaoJDBC import UserDaoJDBC
from src.modelo.dao.PacientesDaoJDBC import PacientesDaoJDBC
from src.modelo.dao.ConstanteDaoJDBC import ConstanteDaoJDBC
from src.modelo.dao.TratamientosDaoJDBC import TratamientosDaoJDBC
from src.modelo.dao.TomasDaoJDBC import TomasDaoJDBC
from src.modelo.dao.CitasDaoJDBC import CitasDaoJDBC
from src.modelo.dao.PacientesDaoJDBC import PacientesDaoJDBC
from src.modelo.dao.PacientesDaoJDBC import PacientesDaoJDBC

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
        from src.modelo.dao.CitasDaoJDBC import CitasDaoJDBC
        dao = CitasDaoJDBC()
        return dao.obtener_agenda(userVO, desde, hasta)

    #def guardarEpisodio(self, episodioVO):
    #    from src.modelo.dao.EpisodiosDaoJDBC import EpisodiosDaoJDBC
    #    dao = EpisodiosDaoJDBC()
    #    dao.guardar_episodio(episodioVO)

    def ingresarPaciente(self, id_paciente, id_medico):
        dao = PacientesDaoJDBC()
        dao.ingresar_paciente(id_paciente, id_medico)

    #def guardarTratamiento(self, tratamientoVO):
    #    from src.modelo.dao.TratamientosDaoJDBC import TratamientosDaoJDBC
    #    dao = TratamientosDaoJDBC()
    #    dao.guardar_tratamiento(tratamientoVO)

    def buscarPaciente(self, texto):
        dao = PacientesDaoJDBC()
        return dao.buscar_paciente(texto)

    #def obtenerEpisodios(self, id_paciente):
    #    from src.modelo.dao.EpisodiosDaoJDBC import EpisodiosDaoJDBC
    #    dao = EpisodiosDaoJDBC()
    #    return dao.obtener_episodios(id_paciente)


