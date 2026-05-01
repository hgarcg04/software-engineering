from src.modelo.Conexion.Conexion import Conexion
from src.modelo.VO.CitasVO import CitaVO

class CitasDaoJDBC(Conexion):

    SQL_AGENDA_HOY = """
        SELECT c.id_cita, c.fecha, c.hora, px.nombre, px.apellido1, px.apellido2,
            c.motivo, px.id_paciente
        FROM Citas as c
        INNER JOIN Pacientes as px ON c.id_paciente = px.id_paciente
        WHERE c.id_medico = ?
        AND c.fecha = CAST(GETDATE() AS DATE)
        ORDER BY c.hora ASC
    """

    SQL_AGENDA_RANGO = """
        SELECT c.id_cita, c.fecha, c.hora, px.nombre, px.apellido1, px.apellido2,
            c.motivo, px.id_paciente
        FROM Citas as c
        INNER JOIN Pacientes as px ON c.id_paciente = px.id_paciente
        WHERE c.id_medico = ?
        AND c.fecha BETWEEN ? AND ?
        ORDER BY c.fecha ASC, c.hora ASC
    """

    def obtener_agenda_hoy(self, userVO):
        cursor = self.getCursor()
        citas = []
        try:
            cursor.execute(self.SQL_AGENDA_HOY, (userVO.id_empleado,))
            rows = cursor.fetchall()
            for row in rows:
                print(f"Row completa: {row}")
                nombre_completo = f"{row[3]} {row[4]} {row[5]}".strip()
                citaVO = CitaVO(
                    id_cita=row[0],
                    fecha=str(row[1]),
                    hora=str(row[2]),
                    paciente_nombre=nombre_completo, # Atributo extra para la vista
                    motivo=row[6],
                    id_paciente=row[7],
                    id_medico=userVO.id_empleado
                )
                citas.append(citaVO)
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
                    'fecha_hora':  f"{str(row[1])} {str(row[2])}",
                    'paciente':    f"{row[3]} {row[4]} {row[5]}",
                    'motivo':      row[6] if row[6] else '',
                    'id_paciente': row[7]
                })
            return citas
        except Exception as e:
            print("Error obteniendo agenda:", e)
            return []
        
        