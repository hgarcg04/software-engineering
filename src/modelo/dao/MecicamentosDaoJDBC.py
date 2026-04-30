from src.modelo.Conexion.Conexion import Conexion

class MedicamentosDaoJDBC(Conexion):

    SQL_SELECT_TODOS = """
        SELECT id_medicamento, nombre, categoria, stock
        FROM Medicamentos
        ORDER BY nombre ASC
    """

    def obtener_todos(self):
        cursor = self.getCursor()
        medicamentos = []
        try:
            cursor.execute(self.SQL_SELECT_TODOS)
            rows = cursor.fetchall()
            for row in rows:
                medicamentos.append({
                    'id_medicamento': row[0],
                    'nombre':         row[1],
                    'categoria':      row[2] if row[2] else '',
                    'stock':          row[3]
                })
            return medicamentos
        except Exception as e:
            print("Error obteniendo medicamentos:", e)
            return []