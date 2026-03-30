from src.modelo.dao.UserDaoJDBC import UserDaoJDBC

class Logica():

    def ejemploSelect(self):
        userDAO = UserDaoJDBC
        usuarios = userDAO.select()

        for user in usuarios:
            print(user.nombre)
    
    def comprobarLogin(self, loginVO):
        login_dao = UserDaoJDBC()
        return login_dao.consultarLogin(loginVO)


