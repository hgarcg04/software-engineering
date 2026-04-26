class TomaVO:
    def __init__(self, id_enfermero, id_tratamiento, observaciones, id_toma=None, fecha=None, hora=None, id_ingreso=None, nombre=None ):
        self.id_enfermero = id_enfermero
        self.id_tratamiento = id_tratamiento
        self.observaciones = observaciones
        self.id_toma = id_toma
        self.fecha = fecha
        self.hora = hora
        self.id_ingreso = id_ingreso
        self.nombre = nombre

        