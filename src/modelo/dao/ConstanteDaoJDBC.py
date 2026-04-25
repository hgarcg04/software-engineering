from src.modelo.Conexion.Conexion import Conexion


class ConstanteDaoJDBC(Conexion):
    SQL_INSERT = """
                    insert into Constantes (id_episodio, id_enfermero, fecha, hora, Temperatura) 
                    values (?, ?, getdate(), convert(time(0), getdate()), ?)
                """
    
    def guardar_constante(self, ConstanteVO):
        cursor = self.getCursor()
        try:
            cursor.execute(self.SQL_INSERT, (ConstanteVO.id_episodio,
                                              ConstanteVO.id_enfermero, ConstanteVO.valor,))


        except Exception as e:
            print("Error en el insert: ", e)