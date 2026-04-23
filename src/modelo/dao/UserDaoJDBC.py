from src.modelo.Conexion.Conexion import Conexion
from src.modelo.VO.UsuariosV0 import UserVO


class UserDaoJDBC(Conexion):
    SQL_SELECT = "SELECT id_empleado, dni, nombre FROM Personal"

    SQL_CHECK_LOGIN = "SELECT id_empleado, dni, nombre, apellidos, nombre_usuario, email, password_, rol FROM Personal WHERE nombre_usuario = ? AND password_ = ?"

    def consultarLogin(self, loginVO):
        cursor = self.getCursor()
        try:
            cursor.execute(self.SQL_CHECK_LOGIN, (loginVO.nombre, loginVO.passw))
            row = cursor.fetchone()
           

            if row is None:
                return None
            else:
                (
                    id_empleado,
                    dni,
                    nombre,
                    apellidos,
                    nombre_usuario,
                    email,
                    password_,
                    rol,
                ) = row
                return UserVO(nombre, rol, id_empleado)
            
        

        except Exception as e:
            print("Error al consultar login", e)
            return None
        


