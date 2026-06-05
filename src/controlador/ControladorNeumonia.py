class ControladorNeumonia:
    def __init__(self, vista, modelo_ia):
        self._vista = vista
        self._modelo_ia = modelo_ia

    def clasificar_imagen(self, ruta_imagen):
        try:
            resultados = self._modelo_ia.clasificar(ruta_imagen)
            # Coge el resultado con mayor confianza
            mejor = max(resultados, key=lambda x: x['score'])
            label = mejor['label']
            confianza = round(mejor['score'] * 100, 2)
            self._vista.mostrar_resultado(label, confianza)
        except Exception as e:
            self._vista.mostrar_error(str(e))