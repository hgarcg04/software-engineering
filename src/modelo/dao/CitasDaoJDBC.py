from src.modelo.Conexion.Conexion import Conexion
from src.modelo.VO.CitasVO import CitaVO
from src.modelo.VO.UsuariosVO import UserVO

class CitasDaoJDBC(Conexion):

    SQL_AGENDA_HOY = """
        SELECT c.id_cita, c.fecha, c.hora, px.nombre, px.apellido1, px.apellido2,
            px.id_paciente, px.hospitalizado
        FROM Citas as c
        INNER JOIN Pacientes as px ON c.id_paciente = px.id_paciente
        WHERE c.id_medico = ?
        AND c.fecha = CAST(GETDATE() AS DATE)
        ORDER BY c.hora ASC
    """

    SQL_AGENDA_RANGO = """
        SELECT c.id_cita, c.fecha, c.hora, px.nombre, px.apellido1, px.apellido2,
            px.id_paciente
        FROM Citas as c
        INNER JOIN Pacientes as px ON c.id_paciente = px.id_paciente
        WHERE c.id_medico = ?
        AND c.fecha BETWEEN ? AND ?
        ORDER BY c.fecha ASC, c.hora ASC 
    """
    # No se ordena bien la lista de citas totales

    # --- CU4: Asignar Citas ---

    # Especialidades distintas desde la tabla Medicos
    SQL_OBTENER_ESPECIALIDADES = """
        SELECT DISTINCT m.especialidad
        FROM Medicos AS m
        WHERE m.especialidad IS NOT NULL
        ORDER BY m.especialidad ASC
    """

    # Médicos con JOIN entre Personal y Medicos; filtra por especialidad si se indica
    SQL_OBTENER_MEDICOS_POR_ESPECIALIDAD = """
        SELECT p.id_empleado, p.nombre, p.apellidos, m.especialidad
        FROM Personal AS p
        INNER JOIN Medicos AS m ON m.id_medico = p.id_empleado
        WHERE (? IS NULL OR m.especialidad = ?)
        ORDER BY p.apellidos ASC
    """

    # Citas ya confirmadas para un médico en una semana (para el calendario)
    SQL_CITAS_SEMANA = """
        SELECT c.fecha, c.hora, px.nombre, px.apellido1, px.apellido2
        FROM Citas AS c
        INNER JOIN Pacientes AS px ON c.id_paciente = px.id_paciente
        WHERE c.id_medico = ?
        AND c.fecha BETWEEN ? AND ?
        ORDER BY c.fecha ASC, c.hora ASC
    """

    # Comprueba si la fecha cae dentro de algún bloqueo manual del médico
    SQL_DIA_BLOQUEADO = """
        SELECT fecha_inicio, fecha_fin
        FROM BloqueosAgenda
        WHERE id_medico = ?
        AND ? BETWEEN fecha_inicio AND fecha_fin
    """

    # Inserta una nueva cita vinculada a paciente y médico
    SQL_INSERTAR_CITA = """
        INSERT INTO Citas (id_paciente, id_medico, fecha, hora)
        VALUES (?, ?, ?, ?)
    """

    # --- CU9: Bloquear Agenda ---

    # Busca médicos por nombre o apellidos con JOIN a Medicos para obtener la especialidad
    SQL_BUSCAR_MEDICO = """
        SELECT p.id_empleado, p.nombre, p.apellidos, m.especialidad
        FROM Personal AS p
        INNER JOIN Medicos AS m ON m.id_medico = p.id_empleado
        WHERE (p.nombre LIKE ? OR p.apellidos LIKE ?)
        ORDER BY p.apellidos ASC
    """

    # Cuenta citas ya asignadas en el rango de fechas a bloquear
    SQL_CITAS_EN_RANGO = """
        SELECT COUNT(*)
        FROM Citas
        WHERE id_medico = ?
        AND fecha BETWEEN ? AND ?
    """

    # Inserta el bloqueo de agenda para un médico en un rango de fechas
    SQL_INSERTAR_BLOQUEO = """
        INSERT INTO BloqueosAgenda (id_medico, fecha_inicio, fecha_fin, motivo, observaciones)
        VALUES (?, ?, ?, ?, ?)
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
                    paciente_nombre=nombre_completo,
                    motivo="",
                    id_paciente=row[6],
                    id_medico=userVO.id_empleado,
                    hospitalizado=row[7]
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
                citaVO = CitaVO(
                    id_cita = row[0],
                    fecha = row[1],
                    hora = row[2],
                    id_paciente = row[6],
                    id_medico=userVO.id_empleado,
                    paciente_nombre = f"{row[3]} {row[4]} {row[5]}",
                    motivo = ""
                )
                citas.append(citaVO)
            return citas
        except Exception as e:
            print("Error obteniendo agenda:", e)
            return []

    # --- CU4: Asignar Citas ---

    def obtener_especialidades(self):
        # Devuelve la lista de especialidades para poblar el combo de la vista
        cursor = self.getCursor()
        try:
            cursor.execute(self.SQL_OBTENER_ESPECIALIDADES)
            return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            print("Error obteniendo especialidades:", e)
            return []

    def obtener_medicos_por_especialidad(self, especialidad=None):
        cursor = self.getCursor()
        try:
            cursor.execute(self.SQL_OBTENER_MEDICOS_POR_ESPECIALIDAD,
                           (especialidad, especialidad))
            rows = cursor.fetchall()
            return [
                UserVO(
                    id_empleado=row[0],
                    dni=None,
                    nombre=row[1],
                    apellidos=row[2],
                    email=None,
                    rol='medico',
                    estado=None,
                    especialidad=row[3]
                )
                for row in rows
            ]
        except Exception as e:
            print("Error obteniendo médicos:", e)
            return []
        
    @staticmethod
    def _hora_a_str(valor):
        """
        Convierte el valor de hora devuelto por jaydebeapi/JDBC a string 'HH:MM'.
        JDBC devuelve java.sql.Time, que jaydebeapi convierte a datetime.time o str
        con formato variable ('HH:MM:SS' o 'HH:MM'). Normalizamos siempre a 'HH:MM'.
        """
        if valor is None:
            return None
        s = str(valor)
        # Elimina microsegundos si los hay: '08:00:00.0' → '08:00:00'
        s = s.split('.')[0]
        # Toma solo HH:MM
        partes = s.strip().split(':')
        if len(partes) >= 2:
            return f"{partes[0].zfill(2)}:{partes[1].zfill(2)}"
        return s[:5]

    def obtener_citas_semana(self, id_medico, fecha_inicio, fecha_fin):
        """
        Devuelve lista de dicts con las citas de la semana para el calendario.
        Cada dict: {fecha, hora, paciente, motivo}
        """
        cursor = self.getCursor()
        try:
            cursor.execute(self.SQL_CITAS_SEMANA, (id_medico, str(fecha_inicio), str(fecha_fin)))
            rows = cursor.fetchall()
            citas = []
            for row in rows:
                citas.append({
                    'fecha': str(row[0]),
                    'hora':  self._hora_a_str(row[1]),
                    'paciente': f"{row[2]} {row[3]} {row[4]}".strip()
                })
            return citas
        except Exception as e:
            print("Error obteniendo citas semana:", e)
            return []

    def obtener_dias_bloqueados_semana(self, id_medico, fecha_inicio, fecha_fin):
        """
        Devuelve el conjunto de fechas (str 'YYYY-MM-DD') bloqueadas en la semana.
        """
        cursor = self.getCursor()
        try:
            # Traemos todos los bloqueos que solapan con la semana
            cursor.execute("""
                SELECT fecha_inicio, fecha_fin
                FROM BloqueosAgenda
                WHERE id_medico = ?
                AND fecha_fin >= ? AND fecha_inicio <= ?
            """, (id_medico, str(fecha_inicio), str(fecha_fin)))
            rows = cursor.fetchall()
            from datetime import date, timedelta
            bloqueados = set()
            semana = [fecha_inicio + timedelta(days=i)
                      for i in range((fecha_fin - fecha_inicio).days + 1)]
            for row in rows:
                fi = row[0] if isinstance(row[0], date) else date.fromisoformat(str(row[0]))
                ff = row[1] if isinstance(row[1], date) else date.fromisoformat(str(row[1]))
                for d in semana:
                    if fi <= d <= ff:
                        bloqueados.add(str(d))
            return bloqueados
        except Exception as e:
            print("Error obteniendo días bloqueados:", e)
            return set()

    def asignar_cita(self, id_paciente, id_medico, fecha, hora):
        # Inserta la cita. Fechas y horas se pasan como str porque jaydebeapi
        # no acepta datetime.date directamente con el driver MSSQL JDBC.
        cursor = self.getCursor()
        try:
            #print(f"EJECUTANDO INSERT CITA")

            cursor.execute(self.SQL_INSERTAR_CITA,
                           (id_paciente, id_medico, str(fecha), str(hora)))
            self.conexion.commit()
            return True, "Cita asignada correctamente."
        except Exception as e:
            self.conexion.rollback()
            print("Error asignando cita:", e)
            return False, f"Error al asignar la cita: {e}"

    # --- CU9: Bloquear Agenda ---

    def buscar_medico(self, texto):
        cursor = self.getCursor()
        try:
            patron = f"%{texto}%"
            cursor.execute(self.SQL_BUSCAR_MEDICO, (patron, patron))
            rows = cursor.fetchall()
            return [
                UserVO(
                    id_empleado=row[0],
                    dni=None,
                    nombre=row[1],
                    apellidos=row[2],
                    email=None,
                    rol='medico',
                    estado=None,
                    especialidad=row[3]
                )
                for row in rows
            ]
        except Exception as e:
            print("Error buscando médico:", e)
            return []

    def hay_citas_en_rango(self, id_medico, fecha_inicio, fecha_fin):
        # Devuelve True si existe al menos una cita en el rango, impidiendo el bloqueo
        cursor = self.getCursor()
        try:
            cursor.execute(self.SQL_CITAS_EN_RANGO,
                           (id_medico, str(fecha_inicio), str(fecha_fin)))
            row = cursor.fetchone()
            return row and row[0] > 0
        except Exception as e:
            print("Error comprobando citas en rango:", e)
            return False

    def bloquear_agenda(self, id_medico, fecha_inicio, fecha_fin, motivo, observaciones):
        # Inserta el bloqueo. Fechas como str por compatibilidad con jaydebeapi/JDBC.
        cursor = self.getCursor()
        try:
            cursor.execute(self.SQL_INSERTAR_BLOQUEO,
                           (id_medico, str(fecha_inicio), str(fecha_fin), motivo, observaciones))
            self.conexion.commit()
            return True, "Agenda bloqueada correctamente."
        except Exception as e:
            self.conexion.rollback()
            print("Error bloqueando agenda:", e)
            return False, f"Error al bloquear la agenda: {e}"