import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from PyQt5.QtWidgets import QDialog, QVBoxLayout

class LogicaGenerarGrafica:

    def generar_grafico(self, df_constantes, tomas, rangos, id_episodio, tipo):
        con_valor = df_constantes.dropna(subset=['valor'])
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

        for toma, medicamento in tomas:
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

        dialogo = QDialog()
        dialogo.setWindowTitle(f"Gráfica - {tipo}")
        layout = QVBoxLayout()
        canvas = FigureCanvas(fig)
        toolbar = NavigationToolbar(canvas, dialogo)
        layout.addWidget(toolbar)
        layout.addWidget(canvas)
        dialogo.setLayout(layout)
        dialogo.resize(900, 400)
        dialogo.exec_()
