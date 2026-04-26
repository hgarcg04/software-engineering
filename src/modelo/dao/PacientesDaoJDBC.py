from src.modelo.Conexion.Conexion import Conexion
from src.modelo.VO.PacientesVO import PacientesVO
from src.modelo.VO.UsuariosVO import UserVO


class PacientesDaoJDBC(Conexion):
    SQL_SELECT = """SELECT  ep.id_episodio, px.nif, px.nombre, px.apellido1, px.apellido2, 
                            px.fecha_nacimiento, px.genero, px.fecha_registro, 
                            med.apellidos, I.num_habitacion, ep.fecha_hora_inicio,
                            I.dieta, I.id_ingreso

                    FROM Ingreso_Enfermeros as IE

                    inner join Ingresos as I on IE.id_ingreso = I.id_ingreso
                    inner join Episodios as ep on I.id_episodio = ep.id_episodio
                    inner join Pacientes as px on ep.id_paciente = px.id_paciente
                    inner join Personal as med on px.medico_asignado = med.id_empleado
                    
                    WHERE IE.id_enfermero = ? AND px.hospitalizado = 1 """

    def devuelve_pacientes_ingresados(self, UserVO):
        cursor = self.getCursor()
        pacientes = []
        try:

            cursor.execute(self.SQL_SELECT, (UserVO.id_empleado,))
            rows = cursor.fetchall()

            for row in rows:
                paciente = PacientesVO(
                    id_episodio=row[0],
                    nif=row[1],
                    nombre=row[2],
                    apellido1=row[3],
                    apellido2=row[4],
                    fecha_nacimiento=row[5],
                    genero=row[6],
                    fecha_registro=row[7],
                    medico_asignado=row[8],
                    num_habitacion=row[9],
                    fecha_ingreso=row[10],
                    dieta=row[11],
                    id_ingreso=row[12]
                )
                pacientes.append(paciente)

            return pacientes

        except Exception as e:
            print("Error", e)
            return []
