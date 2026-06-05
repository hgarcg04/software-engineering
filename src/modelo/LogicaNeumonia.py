from transformers import pipeline
from PIL import Image

class LogicaNeumonia:
    def __init__(self):
        self._clasificador = pipeline(
            "image-classification",
            model="nickmuchi/vit-finetuned-chest-xray-pneumonia"
        )

    def clasificar(self, ruta_imagen):
        imagen = Image.open(ruta_imagen).convert("RGB")
        resultados = self._clasificador(imagen)
        # Devuelve lista de dicts [{'label': 'PNEUMONIA', 'score': 0.98}, ...]
        return resultados