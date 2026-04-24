from src.modelo.dao.UserDaoJDBC import UserDaoJDBC
from src.modelo.dao.PacientesDaoJDBC import PacientesDaoJDBC

class Logica():
    
    def comprobarLogin(self, loginVO):
        login_dao = UserDaoJDBC()
        return login_dao.consultarLogin(loginVO)


    def obtenerPacientes(self):
            paciente_dao = PacientesDaoJDBC()
            return paciente_dao.devuelve_pacientes_ingresados()