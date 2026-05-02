from src.modelo.Conexion.Conexion import Conexion
from src.modelo.VO.EpisodiosVO import EpisodioVO

class EpisodiosDaoJDBC(Conexion):

    SQL_INSERT_EPISODIO = """
        INSERT INTO Episodios (id_paciente, fecha_hora_inicio, tipo)
        OUTPUT INSERTED.id_episodio
        VALUES (?, GETDATE(), ?)
    """

    SQL_INSERT_CONSULTA = """
        INSERT INTO Consultas (id_episodio, diagnostico)
        VALUES (?, ?)
    """
    # Cuando añadamos los sintomas habrá que añadirlo también

    SQL_INSERT_EPISODIO_INGRESO = """
        INSERT INTO Episodios (id_paciente, fecha_hora_inicio, tipo)
        OUTPUT INSERTED.id_episodio
        VALUES (?, GETDATE(), 'Ingreso')
    """

    SQL_INSERT_INGRESO = """
        INSERT INTO Ingresos (id_episodio)
        VALUES (?)
    """

    SQL_UPDATE_HOSPITALIZADO = """
        UPDATE Pacientes SET hospitalizado = 1
        WHERE id_paciente = ?
    """

    SQL_SELECT_EPISODIOS = """
                            SELECT ep.id_paciente, px.medico_asignado, c.diagnostico, ep.tipo, ep.id_episodio, ep.fecha_hora_inicio,
                            ep.fecha_hora_fin, med.apellidos
                                    
                            FROM Episodios as ep
                            LEFT JOIN Consultas as c ON ep.id_episodio = c.id_episodio
                            INNER join Pacientes as px ON ep.id_paciente = px.id_paciente
                            INNER join Personal as med ON px.medico_asignado = med.id_empleado
                            WHERE ep.id_paciente = ?
                            ORDER BY ep.fecha_hora_inicio DESC

                            """

    SQL_SELECT_DETALLE_EPISODIO = """
        SELECT ep.id_episodio, ep.fecha_hora_inicio, ep.fecha_hora_fin, ep.tipo,
            c.diagnostico
        FROM Episodios as ep
        LEFT JOIN Consultas as c ON ep.id_episodio = c.id_episodio
        WHERE ep.id_episodio = ?
    """

    SQL_INSERT_CONSULTA_EXISTENTE = """
        INSERT INTO Consultas (id_episodio, diagnostico)
        VALUES (?, ?)
    """

    def guardar_episodio(self, episodioVO):
        cursor = self.getCursor()
        try:
            # 1. Insertar en Episodios y obtener el id generado
            cursor.execute(self.SQL_INSERT_EPISODIO, (
                episodioVO.id_paciente,
                episodioVO.tipo
            ))
            row = cursor.fetchone()
            id_episodio = row[0]

            # 2. Insertar en Consultas con el diagnóstico
            cursor.execute(self.SQL_INSERT_CONSULTA, (
                id_episodio,
                episodioVO.diagnostico
            )) # Aquí también habrá que cambiarlo

            self.conexion.commit()
            print("Episodio y consulta guardados con éxito")
            return id_episodio

        except Exception as e:
            print("Error guardando episodio:", e)
            self.conexion.rollback()
            return None
        
    def ingresar_paciente(self, id_paciente):
        cursor = self.getCursor()
        try:
            # 1. Crear episodio de tipo Ingreso
            cursor.execute(self.SQL_INSERT_EPISODIO_INGRESO, (id_paciente,))
            id_episodio = cursor.fetchone()[0]

            # 2. Crear el ingreso vinculado al episodio
            cursor.execute(self.SQL_INSERT_INGRESO, (id_episodio,))

            # 3. Marcar al paciente como hospitalizado
            cursor.execute(self.SQL_UPDATE_HOSPITALIZADO, (id_paciente,))

            self.conexion.commit()
            print("Paciente ingresado con éxito")

        except Exception as e:
            print("Error ingresando paciente:", e)
            self.conexion.rollback()    

    def obtener_episodios(self, id_paciente):
        cursor = self.getCursor()
        episodios = []
        try:
            cursor.execute(self.SQL_SELECT_EPISODIOS, (id_paciente,))
            rows = cursor.fetchall()
            for row in rows:
                episodio = EpisodioVO(id_paciente=row[0], id_medico=row[1], diagnostico=row[2],
                                      tipo=row[3], id_episodio=row[4], fecha_hora_inicio=row[5],
                                       fecha_hora_fin=row[6], med_apellidos=row[7])
                episodios.append(episodio)

            return episodios
        except Exception as e:
            print("Error obteniendo episodios:", e)
            return []

    def obtener_detalle_episodio(self, id_episodio):
        cursor = self.getCursor()
        try:
            cursor.execute(self.SQL_SELECT_DETALLE_EPISODIO, (id_episodio,))
            row = cursor.fetchone()
            if row:
                return {
                    'id_episodio':  row[0],
                    'fecha':        str(row[1])[:16],
                    'fecha_fin':    str(row[2])[:16] if row[2] else 'Abierto',
                    'tipo':         row[3] if row[3] else '',
                    'diagnostico':  row[4] if row[4] else ''
                }
            return None
        except Exception as e:
            print("Error obteniendo detalle episodio:", e)
            return None
        
    def guardar_consulta_en_episodio(self, id_episodio, diagnostico, sintomas=None):
        cursor = self.getCursor()
        try:
            cursor.execute(self.SQL_INSERT_CONSULTA_EXISTENTE, (id_episodio, diagnostico))
            self.conexion.commit()
            print("Consulta añadida a episodio existente con éxito")
        except Exception as e:
            print("Error guardando consulta en episodio existente:", e)
            self.conexion.rollback()