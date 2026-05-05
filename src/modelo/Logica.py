from src.modelo.dao.UserDaoJDBC import UserDaoJDBC
from src.modelo.dao.ConstanteDaoJDBC import ConstanteDaoJDBC
from src.modelo.dao.TratamientosDaoJDBC import TratamientosDaoJDBC
from src.modelo.dao.TomasDaoJDBC import TomasDaoJDBC
from src.modelo.dao.CitasDaoJDBC import CitasDaoJDBC
from src.modelo.dao.PacientesDaoJDBC import PacientesDaoJDBC
from src.modelo.dao.MedicamentosDaoJDBC import MedicamentosDaoJDBC
from src.modelo.dao.EpisodiosDaoJDBC import EpisodiosDaoJDBC

import pandas as pd

import matplotlib
matplotlib.use('Qt5Agg')

import matplotlib.pyplot as plt
import matplotlib.dates as mdates


class Logica():
    
    def comprobarLogin(self, loginVO):
        login_dao = UserDaoJDBC()
        return login_dao.consultarLogin(loginVO)
    
    def obtenerPacientes(self, UserVO):
        paciente_dao = PacientesDaoJDBC()
        return paciente_dao.devuelve_pacientes_ingresados(UserVO)
    
    def guardarConstante(self, constanteVO):
        constante_dao = ConstanteDaoJDBC()
        constante_dao.guardar_constante(constanteVO)
    
    def consultarHistoricoConstantes(self, id_episodio, tipo, desde, hasta):
        constante_dao = ConstanteDaoJDBC()
        return constante_dao.consultar_historico(id_episodio, tipo, desde, hasta)
    
    def obtenerTratamientos(self, pacienteVO):
        tratamiento_dao = TratamientosDaoJDBC()
        return tratamiento_dao.devuelve_tratamientos(pacienteVO)

    def guardarNuevaToma(self, tomaVO):
        toma_dao = TomasDaoJDBC()
        toma_dao.guardar_nueva_toma(tomaVO)
    
    def obtenerUltimaToma(self, tratamientoVO):
        toma_dao = TomasDaoJDBC()
        return toma_dao.obtener_ultima_toma(tratamientoVO)
     
    def obtenerTomasSesionActual(self, pacienteVO):
        toma_dao = TomasDaoJDBC()
        return toma_dao.obtener_tomas_sesion_actual(pacienteVO)
    
    def obtenerAgendaHoy(self, userVO):
        dao = CitasDaoJDBC()
        return dao.obtener_agenda_hoy(userVO)

    def obtenerAgenda(self, userVO, desde, hasta):
        dao = CitasDaoJDBC()
        return dao.obtener_agenda(userVO, desde, hasta)

    def guardarEpisodio(self, episodioVO):
        dao = EpisodiosDaoJDBC()
        dao.guardar_episodio(episodioVO)

    def ingresarPaciente(self, id_paciente, id_medico):
        dao = PacientesDaoJDBC()
        dao.ingresar_paciente(id_paciente, id_medico)

    def guardarTratamiento(self, tratamientoVO):
        dao = TratamientosDaoJDBC()
        dao.guardar_tratamiento(tratamientoVO)

    def buscarPaciente(self, texto):
        dao = PacientesDaoJDBC()
        return dao.buscar_paciente(texto)

    def obtenerEpisodios(self, id_paciente):
        dao = EpisodiosDaoJDBC()
        return dao.obtener_episodios(id_paciente)
    
    def guardarConsultaEnEpisodio(self, id_episodio, diagnostico, sintomas=None):
        dao = EpisodiosDaoJDBC()
        dao.guardar_consulta_en_episodio(id_episodio, diagnostico, sintomas)
    
    def obtenerTratamientos_por_episodio(self, id_episodio):
        dao = TratamientosDaoJDBC()
        return dao.obtener_tratamientos_por_episodio(id_episodio)
    
    def obtenerMedicamentos(self):
        dao = MedicamentosDaoJDBC()
        return dao.obtener_medicamentos()
    
    def buscarPacientePorId(self, id_paciente):
        dao = PacientesDaoJDBC()
        return dao.buscar_paciente_por_id(id_paciente)

    def actualizarStock(self, id_medicamento, cantidad):
        dao = MedicamentosDaoJDBC()
        dao.actualizar_stock(id_medicamento, cantidad)

    def registrarPaciente(self, pacienteVO):
        dao = PacientesDaoJDBC()
        if dao.existe_paciente(pacienteVO.nif):
            return False, "El paciente ya está registrado"
        
        dao.registrar_paciente(pacienteVO)
        return True, "Paciente registrado correctamente"

    def obtenerConstantesComoDataFrame(self, id_episodio, tipo, desde, hasta):
        dao = ConstanteDaoJDBC()
        constantes = dao.consultar_historico(id_episodio, tipo, desde, hasta)
        df = pd.DataFrame([{
            'datetime': pd.to_datetime(str(c.fecha) + ' ' + str(c.hora)),
            'tipo': c.tipo,
            'valor': c.valor,
        } for c in constantes])
        return df

    # DUDA: esta funcionalidad aquí?

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

