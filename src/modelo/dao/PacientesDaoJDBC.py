from src.modelo.Conexion.Conexion import Conexion
from src.modelo.VO.PacientesVO import PacientesVO
from src.modelo.VO.UsuariosVO import UserVO


class PacientesDaoJDBC(Conexion):
    SQL_SELECT = """SELECT  ep.id_episodio, px.nif, px.nombre, px.apellido1, px.apellido2, 
                            px.fecha_nacimiento, px.genero, px.fecha_registro, 
                            med.apellidos, I.num_habitacion, ep.fecha_hora_inicio,
                            I.dieta, I.id_ingreso, px.id_paciente, I.fecha_inicio, I.hora_inicio,
							I.fecha_fin, I.hora_fin, I.Observaciones

                    FROM Ingreso_Enfermeros as IE

                    inner join Ingresos as I on IE.id_ingreso = I.id_ingreso
                    inner join Episodios as ep on I.id_episodio = ep.id_episodio
                    inner join Pacientes as px on ep.id_paciente = px.id_paciente
                    inner join Personal as med on px.medico_asignado = med.id_empleado
                    
                    WHERE IE.id_enfermero = ? AND px.hospitalizado = 1 """
    
    SQL_BUSCAR_PACIENTE = """
        SELECT px.id_paciente, px.nif, px.nombre, px.apellido1, px.apellido2,
            px.fecha_nacimiento, px.genero, px.fecha_registro, per.apellidos
        FROM Pacientes as px
        LEFT JOIN Personal as per ON px.medico_asignado = per.id_empleado
        WHERE px.nif LIKE ? OR px.nombre LIKE ? OR px.apellido1 LIKE ? OR px.apellido2 LIKE ?
    """

    SQL_BUSCAR_POR_ID = """
        SELECT px.id_paciente, px.nif, px.nombre, px.apellido1, px.apellido2,
            px.fecha_nacimiento, px.genero, px.fecha_registro, per.apellidos
        FROM Pacientes as px
        LEFT JOIN Personal as per ON px.medico_asignado = per.id_empleado
        WHERE px.id_paciente = ?
    """

    SQL_INGRESAR_PACIENTE = """
        UPDATE Pacientes 
        SET hospitalizado = 1 
        WHERE id_paciente = ?
    """

    SQL_REGISTRAR_PACIENTE = """
            INSERT INTO Pacientes (nif, nombre, apellido1, apellido2,
            fecha_nacimiento, genero, fecha_registro, correo, direccion, alergias, telefono)
            VALUES (?, ?, ?, ?,
            ?, ?, GETDATE(), ?, ?, ?, ?)
        """
    
    SQL_BUSCAR_NIF = "SELECT nif FROM Pacientes WHERE nif = ?"
    

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
                    fecha_inicio_ep=row[10],
                    dieta=row[11],
                    id_ingreso=row[12],
                    id_paciente=row[13],
                    fecha_inicio=row[14],
                    hora_inicio=row[15],
                    fecha_fin=row[16],
                    hora_fin=row[17],
                    observaciones=row[18]
                    
                )
                pacientes.append(paciente)

            return pacientes

        except Exception as e:
            print("Error", e)
            return []
    def buscar_paciente(self, texto):
        cursor = self.getCursor()
        pacientes = []
        try:
            patron = f"%{texto}%"
            cursor.execute(self.SQL_BUSCAR_PACIENTE, (patron, patron, patron, patron))
            rows = cursor.fetchall()
            for row in rows:
                paciente = PacientesVO(
                    id_episodio=None,
                    nif=row[1],
                    nombre=row[2],
                    apellido1=row[3],
                    apellido2=row[4],
                    fecha_nacimiento=row[5],
                    genero=row[6],
                    fecha_registro=row[7],
                    medico_asignado=row[8],
                    id_paciente=row[0]
                )
                pacientes.append(paciente)
            return pacientes
        except Exception as e:
            print("Error buscando paciente:", e)
            return []
        
    def buscar_paciente_por_id(self, id_paciente):
        cursor = self.getCursor()
        try:
            cursor.execute(self.SQL_BUSCAR_POR_ID, (id_paciente,))
            row = cursor.fetchone()
            if row:
                return [PacientesVO(
                    id_episodio=None,
                    nif=row[1],
                    nombre=row[2],
                    apellido1=row[3],
                    apellido2=row[4],
                    fecha_nacimiento=row[5],
                    genero=row[6],
                    fecha_registro=row[7],
                    medico_asignado=row[8],
                    id_paciente=row[0]
                )]
            return []
        except Exception as e:
            print("Error buscando paciente por id:", e)
            return []

    def ingresar_paciente(self, id_paciente, id_medico):
        cursor = self.getCursor()
        try:
            cursor.execute(self.SQL_INGRESAR_PACIENTE, (id_paciente,))
            self.conexion.commit()
            print(f"Paciente {id_paciente} ingresado con éxito.")
        
        except Exception as e:
            self.conexion.rollback()
            print(f"Error al ingresar el paciente: {e}")
        finally:
            cursor.close() # revisar porque esto no lo termino de entender
    
    def existe_paciente(self, nif):
        cursor = self.getCursor()
        cursor.execute(self.SQL_BUSCAR_NIF, (nif,))
        return cursor.fetchone() is not None
    
    def registrar_paciente(self, pacienteVO):
        cursor = self.getCursor()
        try:
            cursor.execute(self.SQL_REGISTRAR_PACIENTE, (
                pacienteVO.nif,
                pacienteVO.nombre,
                pacienteVO.apellido1,
                pacienteVO.apellido2,
                str(pacienteVO.fecha_nacimiento),
                pacienteVO.genero,
                pacienteVO.correo,
                pacienteVO.direccion,
                pacienteVO.alergias, 
                pacienteVO.telefono
            ))
            
        except Exception as e:
            print("Error al registrar paciente: ", e)
       