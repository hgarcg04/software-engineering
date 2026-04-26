class TratamientoVO:
    def __init__(self, id_tratamiento, id_ingreso, id_medico, id_medicamento,
                 dosis, frecuencia, notas, fecha_inicio, fecha_fin, activo,
                 via_administracion, nombre, categoria, descripcion,
                 unidad_medida, stock, stock_minimo, alerta_stock):
        
        self.id_tratamiento = id_tratamiento
        self.id_ingreso = id_ingreso
        self.id_medico = id_medico
        self.id_medicamento = id_medicamento
        self.dosis = dosis
        self.frecuencia = frecuencia
        self.notas = notas
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.activo = activo
        self.via_administracion = via_administracion

        self.nombre = nombre
        self.categoria = categoria
        self.descripcion = descripcion
        self.unidad_medida = unidad_medida
        self.stock = stock
        self.stock_minimo = stock_minimo
        self.alerta_stock = alerta_stock