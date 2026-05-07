


from src.modelo.Conexion.Conexion import Conexion
from src.modelo.VO.TomaVO import TomaVO


class TomasDaoJDBC(Conexion):
    SQL_INSERT = """
                insert into Tomas (id_tratamiento, id_enfermero, fecha, hora, observaciones) 
                values (?, ?, CAST(GETDATE() AS DATE), CAST(GETDATE() AS TIME), ?)

            
                 """
                 
    
    SQL_SELECT_HOY = """  
                select tomas.id_toma, tomas.fecha, tomas.hora, tomas.id_enfermero,
		        I.id_ingreso, tomas.observaciones, T.id_tratamiento, M.nombre
                from Tomas 
                inner join Tratamientos as T on tomas.id_tratamiento = T.id_tratamiento
                inner join Ingresos as I on T.id_ingreso = I.id_ingreso
				inner join Medicamentos as M on T.id_medicamento = M.id_medicamento
                where T.id_ingreso = ? and tomas.fecha = CAST(GETDATE() AS Date)
				order by tomas.fecha desc, tomas.hora desc
                  """
    
    SQL_SELECT_ULTIMA = """  
                select TOP 1 tomas.id_toma, tomas.fecha, tomas.hora, tomas.id_enfermero, I.id_ingreso, 
                tomas.observaciones, T.id_tratamiento
                from Tomas 
                inner join Tratamientos as T on tomas.id_tratamiento = T.id_tratamiento
                inner join Ingresos as I on T.id_ingreso = I.id_ingreso
                where T.id_tratamiento = ?
                order by tomas.fecha desc, tomas.hora desc
                  """

    SQL_SELECT_TOMAS_EPISODIO = """
    
                select tomas.id_toma, tomas.fecha, tomas.hora, tomas.id_enfermero,
                            I.id_ingreso, tomas.observaciones, T.id_tratamiento, M.nombre
                            from Tomas
                            inner join Tratamientos as T on tomas.id_tratamiento = T.id_tratamiento
                            inner join Ingresos as I on T.id_ingreso = I.id_ingreso
                            inner join Medicamentos as M on T.id_medicamento = M.id_medicamento
                            where I.id_episodio = ?
                            order by tomas.fecha desc, tomas.hora desc
                    
                                """

    def guardar_nueva_toma(self, tomaVO):
        cursor = self.getCursor()
        try:
            cursor.execute(self.SQL_INSERT, (tomaVO.id_tratamiento, tomaVO.id_enfermero, tomaVO.observaciones,))
        except Exception as e:
            print("Error al insertar nueva toma", e)
    
    def obtener_tomas_sesion_actual(self, pacienteVO):
            cursor = self.getCursor()
            tomas = []
            try:
                # Ejecutamos la consulta filtrada directamente en SQL
                print(f"se piden las tomas de hoy del ingreso con id {pacienteVO.id_ingreso}")
                cursor.execute(self.SQL_SELECT_HOY, (pacienteVO.id_ingreso,))
                rows = cursor.fetchall()
                for row in rows:
                    toma = TomaVO(id_toma=row[0], fecha=row[1], hora=row[2], id_enfermero=row[3], id_ingreso=row[4],
                                observaciones=row[5], id_tratamiento=row[6], nombre=row[7])
                    tomas.append(toma)
                return tomas
            except Exception as e:
                print("Error al obtener tomas de hoy: ", e)
                return [] 
    

        
    def obtener_ultima_toma(self, tratamientoVO):
        cursor = self.getCursor()
        try:
            # Ejecutamos la consulta para traer solo 1 registro
            cursor.execute(self.SQL_SELECT_ULTIMA, (tratamientoVO.id_tratamiento,))
            row = cursor.fetchone() # Usamos fetchone porque solo esperamos un resultado
            
            if row:
                return TomaVO(id_toma=row[0], fecha=row[1], hora=row[2], id_enfermero=row[3], id_ingreso=row[4],
                              observaciones=row[5], id_tratamiento=row[6])
        except Exception as e:
            print("Error al obtener la última toma: ", e)
        
        return None

    def obtener_tomas_epidio(self, PacienteVO):
        cursor = self.getCursor()
        try:
            cursor.execute(self.SQL_SELECT_TOMAS_EPISODIO, (PacienteVO.id_epidio),)
        except Exception as e:
            print(e)
        