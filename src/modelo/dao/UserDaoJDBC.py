from src.modelo.Conexion.Conexion import Conexion
from src.modelo.VO.UsuariosV0 import UserVO
class UserDaoJDBC(Conexion):
    SQL_SELECT = "SELECT id_empleado, dni, nombre FROM Empleados"
    SQL_INSERT = ""
    SQL_CHECK_LOGIN = "SELECT * FROM Personal WHERE nombre_usuario = ? AND password_ "

    def consultarLogin(self, loginVO):
        cursor = self.getCursor()
        try:
            cursor.execute(self.SQL_LOGIN, (loginVO.nombre, loginVO.passw))
            row = cursor.fetchone()

            if row == None:
                return None
            else:
                id_empleado, dni, nombre = row
                usuario = UserVO(id_empleado, dni, nombre)
                return usuario


        except Exception as e:
            print(e)


    def select(self):
        cursor = self.getCursor()
        users = []

        try: 
            cursor.execute(self.SQL_SELECT)
            rows = cursor.fetchall()

            for row in rows:
                id_empleado, dni, nombre = row

        except Exception as e:
            print(e)
    
    