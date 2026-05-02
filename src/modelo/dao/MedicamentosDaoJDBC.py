from src.modelo.Conexion.Conexion import Conexion
from src.modelo.VO.MedicamentosVO import MedicamentoVO

class MedicamentosDaoJDBC(Conexion):
    SQL_SELECT = """

                 SELECT id_medicamento, nombre, categoria,
                 descripcion, unidad_medida, stock, stock_minimo, alerta_stock
                 FROM Medicamentos
                 ORDER BY nombre ASC

                 """
    
    SQL_UPDATE_ACTUALIZAR_STOCK = """
                
                                  UPDATE Medicamentos
                                  SET stock = stock + ?
                                  WHERE id_medicamento = ?
                 
                                  """
    
    SQL_UPDATE_ALERTA_STOCK = """

                              UPDATE Medicamentos
                              SET alerta_stock = ?
                              WHERE id_medicamento = ?

                              """

    # Te regalo este método ache, para cuando necesites mostrar el listado de medicamentos.
    def obtener_medicamentos(self):
        cursor = self.getCursor()
        try:
            cursor.execute(self.SQL_SELECT)
            rows = cursor.fetchall()
            medicamentos = []
            for row in rows:
                medicamento = MedicamentoVO(id_medicamento=row[0], nombre=row[1], categoria=row[2],
                                            descripcion=row[3], unidad_medida=row[4], stock=row[5],
                                            stock_minimo=row[6], alerta_stock=row[7])
                medicamentos.append(medicamento)
            return medicamentos
    
        except Exception as e:
            print("Error al obtener medicamentos: ", e)
            return []
        
    def actualizar_stock(self, id_medicamento, cantidad):
        cursor = self.getCursor()
        try:
            print(f"Se han quitado {cantidad} unidades del medicamento con id {id_medicamento}")
            cursor.execute(self.SQL_UPDATE_ACTUALIZAR_STOCK, (cantidad, id_medicamento, ))
        except Exception as e:
            print(f"Error al añadir/quitar {cantidad} unidades del medicamento con id {id_medicamento}: ", e)


    def set_alerta_stock(self, id_medicamento, bit):
        cursor = self.getCursor()
        try:
            cursor.execute(self.SQL_UPDATE_ALERTA_STOCK, (bit, id_medicamento, ))
        except Exception as e:
            print(f"Error al cambiar la alerta de {not bit} a {bit}: ", e)