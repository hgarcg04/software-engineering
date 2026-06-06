from src.modelo.dao.ConstanteDaoJDBC import ConstanteDaoJDBC
from src.modelo.dao.TomasDaoJDBC import TomasDaoJDBC
import pandas as pd

class LogicaGraficas:



    def devolver_datos_grafico(self, id_episodio, tipo, desde, hasta):

        # Rangos preestablecidos (consenso con equipo médico)

        RANGOS = {
            'Temperatura (ºC)': {
                'peligro_bajo': (34.0, 35.0),
                'normal': (35.0, 37.5),
                'aviso': (37.5, 38.5),
                'peligro_alto': (38.5, 42.0)
            },
            'Frecuencia cardíaca (lpm)': {
                'peligro_bajo': (0, 50),
                'normal': (50, 100),
                'aviso': (100, 120),
                'peligro_alto': (120, 250)
            },
            'Presión sistólica (mmHg)': {
                'peligro_bajo': (0, 90),
                'normal': (90, 120),
                'aviso': (120, 140),
                'peligro_alto': (140, 200)
            },
            'Presión diastólica (mmHg)': {
                'peligro_bajo': (0, 60),
                'normal': (60, 80),
                'aviso': (80, 90),
                'peligro_alto': (90, 130)
            },
            'Saturación de oxígeno (%)': {
                'peligro_bajo': (80, 90),
                'aviso': (90, 95),
                'normal': (95, 100),
            },
        }
        print("Tipo:", tipo)
        rangos = RANGOS.get(tipo, {})

        df_constantes = self._obtenerConstantesComoDataFrame(id_episodio, tipo, desde, hasta)
        if df_constantes.empty:
            print(f"No hay datos para {tipo} en el rango indicado.")
            return None, [], rangos

        df_constantes = df_constantes.sort_values('datetime')

        tomas = self._obtenerTomas(id_episodio, desde, hasta)

        print("Rangos (desde logicagraficas):", rangos)
        return df_constantes, tomas, rangos


    def _obtenerConstantesComoDataFrame(self, id_episodio, tipo, desde, hasta):
        dao = ConstanteDaoJDBC()
        constantes = dao.consultar_historico(id_episodio, tipo, desde, hasta)
        df_constantes = pd.DataFrame([{
            'datetime': pd.to_datetime(str(c.fecha) + ' ' + str(c.hora)),
            'tipo': c.tipo,
            'valor': c.valor,
        } for c in constantes])

        return df_constantes

    def _obtenerTomas(self, id_episodio, desde, hasta):
        dao = TomasDaoJDBC()
        tomas_vo = dao.obtener_tomas_epidio(id_episodio, desde, hasta)

        tomas = [
            (pd.Timestamp(str(t.fecha) + ' ' + str(t.hora)), t.nombre)
            for t in tomas_vo if t.fecha and t.hora
        ]

        return tomas



