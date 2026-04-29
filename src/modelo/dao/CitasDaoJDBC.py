from src.modelo.Conexion.Conexion import Conexion

class CitasDaoJDBC(Conexion):

    SQL_AGENDA_HOY = """
        SELECT c.id_cita, c.fecha_hora, px.nombre, px.apellido1, px.apellido2,
               c.motivo, c.estado, px.id_paciente
        FROM Citas as c
        INNER JOIN Pacientes as px ON c.id_paciente = px.id_paciente
        WHERE c.id_medico = ?
          AND CAST(c.fecha_hora AS DATE) = CAST(GETDATE() AS DATE)
        ORDER BY c.fecha_hora ASC
    """

    SQL_AGENDA_RANGO = """
        SELECT c.id_cita, c.fecha_hora, px.nombre, px.apellido1, px.apellido2,
               c.motivo, c.estado, px.id_paciente
        FROM Citas as c
        INNER JOIN Pacientes as px ON c.id_paciente = px.id_paciente
        WHERE c.id_medico = ?
          AND CAST(c.fecha_hora AS DATE) BETWEEN ? AND ?
        ORDER BY c.fecha_hora ASC
    """

    def obtener_agenda_hoy(self, userVO):
        cursor = self.getCursor()
        citas = []
        try:
            cursor.execute(self.SQL_AGENDA_HOY, (userVO.id_empleado,))
            rows = cursor.fetchall()
            for row in rows:
                citas.append({
                    'id_cita':     row[0],
                    'fecha_hora':  str(row[1]),
                    'hora':        str(row[1])[11:16],  # extrae HH:MM
                    'paciente':    f"{row[2]} {row[3]} {row[4]}",
                    'motivo':      row[5] if row[5] else '',
                    'estado':      row[6] if row[6] else '',
                    'id_paciente': row[7]
                })
            return citas
        except Exception as e:
            print("Error obteniendo agenda de hoy:", e)
            return []

    def obtener_agenda(self, userVO, desde, hasta):
        cursor = self.getCursor()
        citas = []
        try:
            cursor.execute(self.SQL_AGENDA_RANGO, (userVO.id_empleado, desde, hasta))
            rows = cursor.fetchall()
            for row in rows:
                citas.append({
                    'id_cita':     row[0],
                    'fecha_hora':  str(row[1]),
                    'paciente':    f"{row[2]} {row[3]} {row[4]}",
                    'motivo':      row[5] if row[5] else '',
                    'estado':      row[6] if row[6] else '',
                    'id_paciente': row[7]
                })
            return citas
        except Exception as e:
            print("Error obteniendo agenda:", e)
            return []