from src.modelo.dao.UserDaoJDBC import UserDaoJDBC
from src.modelo.dao.PacientesDaoJDBC import PacientesDaoJDBC
from src.modelo.dao.ConstanteDaoJDBC import ConstanteDaoJDBC

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