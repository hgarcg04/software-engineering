from src.modelo.Conexion.Conexion import Conexion
from src.modelo.VO.TratamientosVO import TratamientoVO

class TratamientosDaoJDBC(Conexion):
    SQL_SELECT = """
                    select T.id_tratamiento, T.id_ingreso, T.id_medico, M.id_medicamento, T.dosis, T.frecuencia,
                    T.notas, T.fecha_inicio, T.fecha_fin, T.activo, T.via_administracion, M.nombre, M.categoria,
                    M.descripcion, M.unidad_medida, M.stock, M.stock_minimo, M.alerta_stock

                    from Tratamientos as T
                    inner join Medicamentos as M on T.id_medicamento = M.id_medicamento
                    inner join Ingresos as I on T.id_ingreso = I.id_ingreso
                    inner join Episodios as ep on I.id_episodio = ep.id_episodio
                    where ep.id_paciente = ? AND T.id_ingreso = ?
                    AND (T.fecha_fin IS NULL OR T.fecha_fin >= CAST(GETDATE() AS DATE))
					AND T.activo = 1
                
                """
    
    SQL_SELECT_POR_EPISODIO = """
        SELECT T.id_tratamiento, M.nombre, T.dosis, T.frecuencia,
            T.via_administracion, T.activo
        FROM Tratamientos as T
        INNER JOIN Medicamentos as M ON T.id_medicamento = M.id_medicamento
        INNER JOIN Ingresos as I ON T.id_ingreso = I.id_ingreso
        WHERE I.id_episodio = ?
    """

    def devuelve_tratamientos(self, pacienteVO):
        tratamientos = []
        cursor = self.getCursor()
        try:
            cursor.execute(self.SQL_SELECT, (pacienteVO.id_paciente, pacienteVO.id_ingreso,))
            rows = cursor.fetchall()

            for row in rows:
                tratamiento = TratamientoVO(
                    id_tratamiento=row[0], id_ingreso=row[1], id_medico=row[2], id_medicamento=row[3],
                    dosis=row[4], frecuencia=row[5], notas=row[6], fecha_inicio=row[7], fecha_fin=row[8],
                    activo=row[9], via_administracion=row[10], nombre=row[11], categoria=row[12],
                    descripcion=row[13], unidad_medida=row[14], stock=row[15], stock_minimo=row[16],
                    alerta_stock=row[17]
                )
                tratamientos.append(tratamiento)
            return tratamientos

        except Exception as e:
            print("Error al conseguir tratamientos", e)
            return []
        
    def obtener_tratamientos_por_episodio(self, id_episodio):
        cursor = self.getCursor()
        tratamientos = []
        try:
            cursor.execute(self.SQL_SELECT_POR_EPISODIO, (id_episodio,))
            rows = cursor.fetchall()
            for row in rows:
                tratamientos.append({
                    'medicamento': row[1],
                    'dosis':       row[2] if row[2] else '',
                    'frecuencia':  row[3] if row[3] else '',
                    'via':         row[4] if row[4] else '',
                })
            return tratamientos
        except Exception as e:
            print("Error obteniendo tratamientos por episodio:", e)
            return []