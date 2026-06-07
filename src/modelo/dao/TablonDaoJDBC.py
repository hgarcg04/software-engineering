from src.modelo.Conexion.Conexion import Conexion


class TablonDaoJDBC(Conexion):
    """
    DAO para la tabla TablonTareas.
    Medicos y enfermeros insertan tareas; el administrativo las consulta y elimina.
    """

    SQL_OBTENER_TAREAS = """
        SELECT id_tarea, nombre_remitente, rol_remitente, mensaje, fecha, hora
        FROM TablonTareas
        ORDER BY fecha ASC, hora ASC
    """

    SQL_ELIMINAR_TAREA = """
        DELETE FROM TablonTareas
        WHERE id_tarea = ?
    """

    SQL_INSERTAR_TAREA = """
        INSERT INTO TablonTareas (id_remitente, nombre_remitente, rol_remitente, mensaje, fecha, hora)
        VALUES (?, ?, ?, ?, CAST(GETDATE() AS DATE), CAST(GETDATE() AS TIME))
    """

    def obtener_tareas(self):
        """
        Devuelve todas las tareas pendientes ordenadas por fecha y hora.
        Cada fila: (id_tarea, nombre_remitente, rol_remitente, mensaje, fecha, hora)
        """
        cursor = self.getCursor()
        try:
            cursor.execute(self.SQL_OBTENER_TAREAS)
            return cursor.fetchall()
        except Exception as e:
            print(f"TablonDaoJDBC: error obteniendo tareas: {e}")
            return []

    def eliminar_tarea(self, id_tarea):
        """Elimina la tarea con el id dado (marcarla como completada)."""
        cursor = self.getCursor()
        try:
            cursor.execute(self.SQL_ELIMINAR_TAREA, (id_tarea,))
            self.conexion.commit()
            return True
        except Exception as e:
            print(f"TablonDaoJDBC: error eliminando tarea: {e}")
            self.conexion.rollback()
            return False

    def insertar_tarea(self, user_vo, mensaje):
        """Inserta una nueva tarea. Usado por médicos y enfermeros."""
        cursor = self.getCursor()
        try:
            nombre = f"{user_vo.nombre} {user_vo.apellidos}"
            cursor.execute(self.SQL_INSERTAR_TAREA,
                           (user_vo.id_empleado, nombre, user_vo.rol, mensaje))
            self.conexion.commit()
            return True
        except Exception as e:
            print(f"TablonDaoJDBC: error insertando tarea: {e}")
            self.conexion.rollback()
            return False