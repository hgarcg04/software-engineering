class MedicamentoVO:
    def __init__(self, id_medicamento, nombre, categoria,
                descripcion, unidad_medida, stock, stock_minimo, alerta_stock):
        self.id_medicamento = id_medicamento
        self.nombre = nombre
        self.categoria = categoria
        self.descripcion = descripcion
        self.unidad_medida = unidad_medida
        self.stock = stock
        self.stock_minimo = stock_minimo
        self.alerta_stock = alerta_stock
        