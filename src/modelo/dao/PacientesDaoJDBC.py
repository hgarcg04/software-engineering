from src.modelo.Conexion.Conexion import Conexion
from src.modelo.VO.PacientesVO import PacientesVO
from src.modelo.VO.UsuariosV0 import UserVO

class PacientesDaoJDBC(Conexion):
    SQL_SELECT = """SELECT nif, nombre, apellido1, apellido2, 
                        fecha_nacimiento, genero, fecha_registro, 
                        medico_asignado FROM Pacientes 
                        WHERE estado = 'Activo' """
     
    def devuelve_pacientes_ingresados(self):
            cursor = self.getCursor()
            pacientes = []
            try:
                
                cursor.execute(self.SQL_SELECT)
                rows = cursor.fetchall() 

                for row in rows:
                    paciente = PacientesVO(
                        nif=row[0],
                        nombre=row[1],
                        apellido1=row[2],
                        apellido2=row[3],
                        fecha_nacimiento=row[4],
                        genero=row[5],
                        fecha_registro=row[6],
                        medico_asignado=row[7]
                    )
                    pacientes.append(paciente)

                return pacientes

            except Exception as e:
                print("Error", e)
                return [] 