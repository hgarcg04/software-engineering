from src.modelo.dao.UserDaoJDBC import UserDaoJDBC

class Logica():
    
    def comprobarLogin(self, loginVO):
        login_dao = UserDaoJDBC()
        return login_dao.consultarLogin(loginVO)


