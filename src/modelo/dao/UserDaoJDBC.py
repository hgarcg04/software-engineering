from src.modelo.Conexion.Conexion import Conexion
from src.modelo.VO.UsuariosVO import UserVO


class UserDaoJDBC(Conexion):
    SQL_CHECK_LOGIN = "SELECT id_empleado, dni, nombre, apellidos, nombre_usuario, email, password_, rol FROM Personal WHERE nombre_usuario = ? AND password_ = ?"

    def consultarLogin(self, loginVO):
        cursor = self.getCursor()
        try:
            cursor.execute(self.SQL_CHECK_LOGIN, (loginVO.nombre, loginVO.passw))
            row = cursor.fetchone()
           

            if row is None:
                return None
            else:
                (id_empleado, dni, nombre, apellidos, nombre_usuario, email, password_, rol) = row

                return UserVO(id_empleado, dni, nombre, apellidos, email, rol)
            

        except Exception as e:
            print("Error al consultar login", e)
            return None
        


