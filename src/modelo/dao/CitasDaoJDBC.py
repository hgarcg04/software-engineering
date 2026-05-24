from src.modelo.Conexion.Conexion import Conexion
from src.modelo.VO.CitasVO import CitaVO

class CitasDaoJDBC(Conexion):

    SQL_AGENDA_HOY = """
        SELECT c.id_cita, c.fecha, c.hora, px.nombre, px.apellido1, px.apellido2,
            c.motivo, px.id_paciente, px.hospitalizado
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

    # Horas ya ocupadas por citas confirmadas para un médico en una fecha
    SQL_HORAS_OCUPADAS = """
        SELECT hora
        FROM Citas
        WHERE id_medico = ? AND fecha = ?
    """

    # Comprueba si la fecha cae dentro de algún bloqueo manual del médico
    SQL_DIA_BLOQUEADO = """
        SELECT 1
        FROM BloqueosAgenda
        WHERE id_medico = ?
        AND ? BETWEEN fecha_inicio AND fecha_fin
    """

    # Inserta una nueva cita vinculada a paciente y médico
    SQL_INSERTAR_CITA = """
        INSERT INTO Citas (id_paciente, id_medico, fecha, hora, motivo)
        VALUES (?, ?, ?, ?, ?)
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
                    paciente_nombre=nombre_completo, # Atributo extra para la vista
                    motivo=row[6],
                    id_paciente=row[7],
                    id_medico=userVO.id_empleado,
                    hospitalizado=row[8]
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
                    fecha = row[1], # Antes devolvía fecha_hora juntos así que igual me da algún error
                    hora = row[2],
                    id_paciente = row[7],
                    id_medico=userVO.id_empleado,
                    paciente_nombre = f"{row[3]} {row[4]} {row[5]}",
                    motivo = row[6] if row[6] else ""
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
        # Devuelve tuplas (id_empleado, nombre, apellidos, especialidad)
        # Si especialidad es None, devuelve todos los médicos
        cursor = self.getCursor()
        try:
            cursor.execute(self.SQL_OBTENER_MEDICOS_POR_ESPECIALIDAD,
                           (especialidad, especialidad))
            return cursor.fetchall()
        except Exception as e:
            print("Error obteniendo médicos:", e)
            return []

    def consultar_disponibilidad(self, id_medico, fecha):
        # Devuelve las horas libres del médico en esa fecha (franjas de 30 min, 08:00-14:00)
        # Devuelve None si el día entero está bloqueado manualmente
        cursor = self.getCursor()
        try:
            cursor.execute(self.SQL_DIA_BLOQUEADO, (id_medico, fecha))
            if cursor.fetchone():
                return None

            cursor.execute(self.SQL_HORAS_OCUPADAS, (id_medico, fecha))
            horas_ocupadas = {str(row[0])[:5] for row in cursor.fetchall()}

            franjas = [
                f"{h:02d}:{m:02d}"
                for h in range(8, 15)
                for m in (0, 30)
                if not (h == 14 and m == 30)
            ]
            return [h for h in franjas if h not in horas_ocupadas]
        except Exception as e:
            print("Error consultando disponibilidad:", e)
            return []

    def asignar_cita(self, id_paciente, id_medico, fecha, hora, motivo):
        # Inserta la cita y confirma la transacción. Devuelve (bool, mensaje)
        cursor = self.getCursor()
        try:
            cursor.execute(self.SQL_INSERTAR_CITA,
                           (id_paciente, id_medico, fecha, hora, motivo))
            self.conexion.commit()
            return True, "Cita asignada correctamente."
        except Exception as e:
            self.conexion.rollback()
            print("Error asignando cita:", e)
            return False, f"Error al asignar la cita: {e}"

    # --- CU9: Bloquear Agenda ---

    def buscar_medico(self, texto):
        # Búsqueda parcial por nombre o apellidos. Devuelve tuplas (id, nombre, apellidos, especialidad)
        cursor = self.getCursor()
        try:
            patron = f"%{texto}%"
            cursor.execute(self.SQL_BUSCAR_MEDICO, (patron, patron))
            return cursor.fetchall()
        except Exception as e:
            print("Error buscando médico:", e)
            return []

    def hay_citas_en_rango(self, id_medico, fecha_inicio, fecha_fin):
        # Devuelve True si existe al menos una cita en el rango, impidiendo el bloqueo
        cursor = self.getCursor()
        try:
            cursor.execute(self.SQL_CITAS_EN_RANGO,
                           (id_medico, fecha_inicio, fecha_fin))
            row = cursor.fetchone()
            return row and row[0] > 0
        except Exception as e:
            print("Error comprobando citas en rango:", e)
            return False

    def bloquear_agenda(self, id_medico, fecha_inicio, fecha_fin, motivo, observaciones):
        # Inserta el bloqueo y confirma la transacción. Devuelve (bool, mensaje)
        cursor = self.getCursor()
        try:
            cursor.execute(self.SQL_INSERTAR_BLOQUEO,
                           (id_medico, fecha_inicio, fecha_fin, motivo, observaciones))
            self.conexion.commit()
            return True, "Agenda bloqueada correctamente."
        except Exception as e:
            self.conexion.rollback()
            print("Error bloqueando agenda:", e)
            return False, f"Error al bloquear la agenda: {e}"