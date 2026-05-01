from src.modelo.Conexion.Conexion import Conexion
from src.modelo.VO.ConstantesVO import ConstantesVO

class ConstanteDaoJDBC(Conexion):
    SQL_INSERT = """
                    insert into Constantes (id_ingreso, id_enfermero, fecha, hora, tipo, valor, observaciones) 
                    values (?, ?, getdate(), FORMAT(GETDATE(), 'HH:mm'), ?, ?, ?)
                 """
    
            
    
    SQL_SELECT = """ 
                SELECT c.Tipo, Valor,  c.Observaciones, c.id_enfermero, c.id_ingreso, px.nif, ep.id_episodio, c.fecha, c.hora
                FROM Constantes as c

                inner join Ingresos as I on I.id_ingreso = c.id_ingreso
                inner join Episodios as ep on I.id_episodio = ep.id_episodio
                inner join Pacientes as px on ep.id_paciente = px.id_paciente

                WHERE ep.id_episodio = ? AND c.Tipo = ?
                AND CAST(fecha AS DATETIME) + CAST(hora AS DATETIME) BETWEEN ? AND ?
                ORDER BY fecha, hora

                 """
    def guardar_constante(self, ConstanteVO):
        cursor = self.getCursor()
        try:
            cursor.execute(self.SQL_INSERT, (ConstanteVO.id_ingreso,
                                              ConstanteVO.id_enfermero, ConstanteVO.tipo, ConstanteVO.valor, ConstanteVO.observaciones,))

        except Exception as e:
            print("Error en el insert: ", e)

    def consultar_historico(self, id_episodio, tipo, desde, hasta):
        cursor = self.getCursor()
        constantes = []
        try:
            cursor.execute(self.SQL_SELECT, (id_episodio, tipo, desde, hasta,))
            rows = cursor.fetchall()

            for row in rows:
                constante = ConstantesVO(
                    tipo=row[0], valor=row[1], observaciones=row[2], id_enfermero=row[3],
                    id_ingreso=row[4], nif_paciente=row[5], id_episodio=row[6], fecha=row[7], hora=row[8])
                
                constantes.append(constante)
            return constantes
        
        except Exception as e:
            print("Error al consultar constantes: ", e)
            

