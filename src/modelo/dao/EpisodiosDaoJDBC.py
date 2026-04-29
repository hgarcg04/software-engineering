from src.modelo.Conexion.Conexion import Conexion

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