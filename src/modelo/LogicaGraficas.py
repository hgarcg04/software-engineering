from src.modelo.dao.ConstanteDaoJDBC import ConstanteDaoJDBC

import pandas as pd

import matplotlib
matplotlib.use('Qt5Agg')

import matplotlib.pyplot as plt
import matplotlib.dates as mdates


class LogicaGraficas:
    def obtenerConstantesComoDataFrame(self, id_episodio, tipo, desde, hasta):
        dao = ConstanteDaoJDBC()
        constantes = dao.consultar_historico(id_episodio, tipo, desde, hasta)
        df = pd.DataFrame([{
            'datetime': pd.to_datetime(str(c.fecha) + ' ' + str(c.hora)),
            'tipo': c.tipo,
            'valor': c.valor,
        } for c in constantes])
        print(df)
        return df

    def generarGrafico(self, id_episodio, tipo, desde, hasta):

        tomas_prueba = [
            (pd.Timestamp('2026-05-05 00:40:00'), 'Paracetamol 1g'),
            (pd.Timestamp('2026-05-05 00:38:00'), 'Ibuprofeno 650mg'),
        ]

        rangos = {
            'normal': (36.0, 37.5),
            'aviso': (37.5, 38.5),
            'peligro_bajo': (35.0, 36.0),
            'peligro_alto': (38.5, 42.0)
        }

        df = self.obtenerConstantesComoDataFrame(id_episodio, tipo, desde, hasta)

        if df.empty:
            print(f"No hay datos para {tipo} en el rango indicado.")
            return

        df = df.sort_values('datetime')

        con_valor = df.dropna(subset=['valor'])

        fig, ax = plt.subplots(figsize=(12, 4))

        # ---- ZONAS SEGURAS/PELIGROSAS ----
        if rangos:
            if 'normal' in rangos:
                ax.axhspan(rangos['normal'][0], rangos['normal'][1],
                           color='green', alpha=0.1, label='Normal')

            if 'aviso' in rangos:
                ax.axhspan(rangos['aviso'][0], rangos['aviso'][1],
                           color='orange', alpha=0.15, label='Aviso')

            if 'peligro_bajo' in rangos:
                ax.axhspan(rangos['peligro_bajo'][0], rangos['peligro_bajo'][1],
                           color='red', alpha=0.1, label='Peligro')

            if 'peligro_alto' in rangos:
                ax.axhspan(rangos['peligro_alto'][0], rangos['peligro_alto'][1],
                           color='red', alpha=0.1, label='Peligro alto')

        # ---- LINEA DE EVOLUDCIÓN ----
        if not con_valor.empty:
            ax.plot(con_valor['datetime'], con_valor['valor'], marker='o', linewidth=1, markersize=5,
                    color='steelblue')

        # ---- TIMESTAMPS DE TOMAS ----

        for toma, medicamento in tomas_prueba:
            ax.axvline(x=toma, color='purple', linestyle='--', linewidth=1.5, alpha=0.7)
            ax.annotate(
                medicamento,
                xy=(toma, ax.get_ylim()[0]),
                xytext=(5, 5),
                textcoords='offset points',
                fontsize=7,
                color='purple',
                rotation=90,
                va='bottom'
            )

        ax.set_title(f"{tipo} | Episodio: {id_episodio} ", fontsize=12, fontweight='bold')
        ax.set_ylabel('Valor')
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m %H:%M'))
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=30, ha='right')
        fig.tight_layout()
        return fig

    #def obtenerTomasComoDataFrame(self, id_episodio, tipo, desde, hasta):

