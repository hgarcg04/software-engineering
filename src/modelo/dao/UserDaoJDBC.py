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
        

    SQL_EXISTE_DNI = "SELECT id_empleado FROM Personal WHERE dni = ?"

    SQL_INSERT_PERSONAL = """
        INSERT INTO Personal (dni, nombre, apellidos, nombre_usuario, password_, email, rol)
        OUTPUT INSERTED.id_empleado
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """

    SQL_INSERT_MEDICO = "INSERT INTO Medicos (id_medico, especialidad) VALUES (?, ?)"

    SQL_INSERT_ENFERMERO = "INSERT INTO Enfermeros (id_enfermero) VALUES (?)"

    def existe_empleado(self, dni):
        """Devuelve True si el DNI ya esta registrado en Personal."""
        cursor = self.getCursor()
        try:
            cursor.execute(self.SQL_EXISTE_DNI, (dni,))
            return cursor.fetchone() is not None
        except Exception as e:
            print("Error comprobando DNI:", e)
            return False

    def generar_credenciales(self, dni, nombre, apellidos, nombre_usuario,
                              password_generada, email, rol, especialidad=None):
        """
        Inserta el nuevo empleado en Personal y, si es medico o enfermero,
        en su tabla especifica. Devuelve (True, nombre_usuario, password)
        o (False, mensaje_error, None).
        """
        cursor = self.getCursor()
        try:
            cursor.execute(self.SQL_INSERT_PERSONAL,
                           (dni, nombre, apellidos, nombre_usuario,
                            password_generada, email, rol))
            row = cursor.fetchone()
            id_empleado = row[0]

            if rol == 'medico':
                cursor.execute(self.SQL_INSERT_MEDICO, (id_empleado, especialidad))
            elif rol == 'enfermero':
                cursor.execute(self.SQL_INSERT_ENFERMERO, (id_empleado,))

            self.conexion.commit()
            return True, nombre_usuario, password_generada
        except Exception as e:
            self.conexion.rollback()
            print("Error generando credenciales:", e)
            return False, str(e), None