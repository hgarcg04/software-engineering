from src.vista.Medicos.LogicaDialogoReceta import DialogoReceta
from src.vista.Medicos.LogicaDialogoEpisodio import DialogoEpisodio
from src.modelo.VO.EpisodiosVO import EpisodioVO
from src.modelo.VO.TratamientosVO import TratamientoVO
from src.modelo.LogicaNeumonia import LogicaNeumonia
from src.modelo.InformeAltaService import InformeAltaService

from datetime import datetime, timedelta

class ControladorMedicos:
    def __init__(self, vista, modelo, user_vo, controlador_principal=None):
        self._vista = vista
        self._modelo = modelo
        self._user_vo = user_vo
        self.controlador_principal = controlador_principal

        self._episodios_actuales = []
        self._ingresos_actuales = []
        self._altas_recientes = []
        self._paciente_hcd_actual = None
        self._episodio_consulta_actual = None  # EpisodioVO activo en la consulta
        self._paciente_ingreso_actual = None

        self._vista.cargar_datos_iniciales(self._user_vo)
        self._cargar_agenda_hoy()

        self._logica_neumonia = None

    # ── Inicio ───────────────────────────────────────────────────

    def _cargar_agenda_hoy(self):
        lista = self._modelo.obtenerAgendaHoy(self._user_vo)
        if lista:
            self._vista.cargar_agenda_hoy(lista)

    # ── Agenda completa ──────────────────────────────────────────

    def cargar_agenda_completa(self, desde=None, hasta=None):
        if desde is None:
            desde = datetime.now().strftime('%Y-%m-%d')
        if hasta is None:
            hasta = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        lista = self._modelo.obtenerAgenda(self._user_vo, desde, hasta)
        self._vista.cargar_agenda_completa(lista if lista else [])

    # ── Consulta ─────────────────────────────────────────────────

    def abrir_seleccion_episodio(self, cita_vo): # Llamado por LogicaMedicos._abrir_consulta()
        episodios = self._modelo.obtenerEpisodios(cita_vo.id_paciente)

        dialogo = DialogoEpisodio(
            parent=self._vista,
            paciente_nombre=cita_vo.paciente_nombre,
            episodios=episodios if episodios else []
        )

        if dialogo.exec_() == DialogoEpisodio.Accepted:
            if dialogo.resultado == DialogoEpisodio.EPISODIO_EXISTENTE:
                self._episodio_consulta_actual = dialogo.episodio_seleccionado
            else:
                self._episodio_consulta_actual = None  # nuevo, se creará al guardar

            # Navegar a la página de consulta
            self._vista.abrir_pagina_consulta(cita_vo, self._episodio_consulta_actual)

    def guardar_consulta(self, sintomas, diagnostico, tipo, cita):
        if self._episodio_consulta_actual is not None:
            # Añadir nueva consulta a episodio existente
            self._modelo.guardarConsultaEnEpisodio(
                id_episodio=self._episodio_consulta_actual.id_episodio,
                diagnostico=diagnostico,
                sintomas=sintomas
            )
        else:
            # Crear episodio nuevo con su consulta
            episodioVO = EpisodioVO(
                id_paciente=cita.id_paciente,
                id_medico=self._user_vo.id_empleado,
                diagnostico=diagnostico,
                tipo=tipo,
                id_episodio=None,
                fecha_hora_inicio=None,
                med_apellidos=self._user_vo.apellidos,
                sintomas=sintomas
            )
            self._modelo.guardarEpisodio(episodioVO)

        self._episodio_consulta_actual = None  # resetear tras guardar

    def ingresar_paciente(self, id_paciente, habitacion): # este es desde cita
        if self._episodio_consulta_actual is not None:
            id_episodio = self._episodio_consulta_actual.id_episodio
        else:
            # No hay episodio guardado aún, creamos uno de hospitalización
            episodioVO = EpisodioVO(
                id_paciente=id_paciente,
                id_medico=self._user_vo.id_empleado,
                diagnostico=None,
                tipo="Hospitalización",
                id_episodio=None,
                fecha_hora_inicio=None,
                med_apellidos=self._user_vo.apellidos,
                sintomas=None
            )
            id_episodio = self._modelo.guardarEpisodio(episodioVO)

        self._modelo.ingresarPaciente(id_paciente, id_episodio, habitacion)

    def ingresar_paciente_desde_hcd(self, id_paciente, habitacion):
        dialogo = DialogoEpisodio(
            parent=self._vista,
            paciente_nombre=self._paciente_hcd_actual.nombre_completo,
            episodios=self._episodios_actuales
        )

        if dialogo.exec_() == DialogoEpisodio.Accepted:
            if dialogo.resultado == DialogoEpisodio.EPISODIO_EXISTENTE:
                id_episodio = dialogo.episodio_seleccionado.id_episodio
            else:
                episodioVO = EpisodioVO(
                    id_paciente=id_paciente,
                    id_medico=self._user_vo.id_empleado,
                    diagnostico=None,
                    tipo="Hospitalización",
                    id_episodio=None,
                    fecha_hora_inicio=None,
                    med_apellidos=self._user_vo.apellidos,
                    sintomas=None
                )
                id_episodio = self._modelo.guardarEpisodio(episodioVO)

            self._modelo.ingresarPaciente(id_paciente, id_episodio, habitacion)
            self.cargar_episodios_paciente(self._paciente_hcd_actual) # Por si creo un nuevo episodio y así se cambian los botones de dar alta e ingresar solos

    # ── Receta ───────────────────────────────────────────────────

    def abrir_receta(self, cita):
        medicamentos = self._modelo.obtenerMedicamentos()
        dialogo = DialogoReceta(parent=self._vista, cita_vo=cita)
        dialogo.inicializar(
            nombre_paciente=cita.paciente_nombre,
            id_paciente=cita.id_paciente,
            id_ingreso=cita.id_ingreso,
            medicamentos=medicamentos,
            controlador=self
        )
        dialogo.exec_()

    def guardar_receta(self, id_medicamento, dosis, frecuencia, via, fecha_inicio, fecha_fin, notas, id_paciente, id_ingreso):
        tratamientoVO = TratamientoVO(
            id_tratamiento=None,
            id_ingreso=id_ingreso,
            id_medico=self._user_vo.id_empleado,
            id_medicamento=id_medicamento,
            dosis=dosis,
            frecuencia=frecuencia,
            notas=notas,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            activo=True,
            via_administracion=via,
            nombre=None,
            categoria=None,
            descripcion=None,
            unidad_medida=None,
            stock=None,
            stock_minimo=None,
            alerta_stock=None
        )
        self._modelo.guardarTratamiento(tratamientoVO)

    # ── HCD ──────────────────────────────────────────────────────

    def buscar_paciente_hcd(self, texto):
        if len(texto) < 2:
            return
        resultados = self._modelo.buscarPaciente(texto)
        self._vista.cargar_resultados_busqueda_hcd(resultados if resultados else [])

    def cargar_episodios_paciente(self, pacienteVO):
        self._paciente_hcd_actual = pacienteVO
        episodios = self._modelo.obtenerEpisodios(pacienteVO.id_paciente)
        self._episodios_actuales = episodios if episodios else []
        self._vista.cargar_episodios_hcd(pacienteVO.nombre_completo, self._episodios_actuales)

        esta_ingresado = self._modelo.pacienteEstaIngresado(pacienteVO.id_paciente)
        
        if esta_ingresado:
            self._vista.configurar_botones_hospitalizacion(puede_ingresar=False, puede_dar_alta=True)
        else:
            self._vista.configurar_botones_hospitalizacion(puede_ingresar=True, puede_dar_alta=False)

    def cargar_tratamientos_ingreso(self, ingresoVO):
        self._paciente_ingreso_actual = ingresoVO
        tratamientos = self._modelo.obtenerTratamientosPorIngreso(ingresoVO.id_ingreso)
        self._vista.cargar_tratamientos_ingreso(tratamientos if tratamientos else [], ingresoVO.nombre_completo)

    def eliminar_tratamiento(self, id_tratamiento):
        self._modelo.eliminarTratamiento(id_tratamiento)
        self.cargar_tratamientos_ingreso(self._paciente_ingreso_actual)

    def abrir_receta_desde_ingreso(self):
        if not self._paciente_ingreso_actual:
            return
        medicamentos = self._modelo.obtenerMedicamentos()
        dialogo = DialogoReceta(self._vista, self._paciente_ingreso_actual)
        dialogo.inicializar(
            nombre_paciente=self._paciente_ingreso_actual.nombre_completo,
            id_paciente=self._paciente_ingreso_actual.id_paciente,
            id_ingreso=self._paciente_ingreso_actual.id_ingreso,
            medicamentos=medicamentos,
            controlador=self
        )
        dialogo.exec_()
        self.cargar_tratamientos_ingreso(self._paciente_ingreso_actual)

    def eliminar_tratamiento_ingreso(self, fila):
        tratamientos = self._modelo.obtenerTratamientosPorIngreso(
            self._paciente_ingreso_actual.id_ingreso)
        if fila >= len(tratamientos):
            return
        id_tratamiento = tratamientos[fila].id_tratamiento
        self._modelo.eliminarTratamiento(id_tratamiento)
        self.cargar_tratamientos_ingreso(self._paciente_ingreso_actual)

    def cargar_detalle_episodio(self, fila):
        if fila >= len(self._episodios_actuales):
            return
        ep = self._episodios_actuales[fila]
        texto = (
            f"Tipo: {ep.tipo}\n"
            f"Fecha inicio: {ep.fecha_hora_inicio}\n"
            f"Fecha fin: {ep.fecha_hora_fin}\n\n"
            f"Diagnóstico:\n{ep.diagnostico}"
        )
        tratamientos = self._modelo.obtenerTratamientos_por_episodio(ep.id_episodio)
        self._vista.mostrar_detalle_episodio(texto, tratamientos if tratamientos else [])

    def cargar_hcd_desde_agenda(self, id_paciente):
        paciente = self._modelo.buscarPacientePorId(id_paciente)
        if paciente:
            self.cargar_episodios_paciente(paciente.id_paciente)

    def dar_alta_paciente(self, diagnostico_alta):
        if not self._paciente_hcd_actual:
            self._vista.mostrar_notificacion(
                "Atención", 
                "No hay ningún paciente seleccionado para dar de alta.", 
                es_error=True
            )
            return
        exito = self._modelo.darAltaMedica(self._paciente_hcd_actual.id_paciente)

        if exito:
            self._vista.mostrar_notificacion(
                "Alta Procesada", 
                f"El paciente {self._paciente_hcd_actual.nombre} ha sido dado de alta correctamente."
            )
            
            self.exportar_informe_alta_pdf(self._paciente_hcd_actual, diagnostico_alta)
            
            self._vista.configurar_botones_hospitalizacion(puede_ingresar=True, puede_dar_alta=False)
            self.cargar_episodios_paciente(self._paciente_hcd_actual)
        else:
            self._vista.mostrar_notificacion(
                "Error de Base de Datos", 
                "No se pudo registrar el alta. Verifique la conexión.", 
                es_error=True
            )

    def exportar_informe_alta_pdf(self, pacienteVO, diagnostico_alta_reciente=None):
        if not pacienteVO:
            return

        ruta = self._vista.solicitar_ruta_informe_alta(pacienteVO.nif)
        if not ruta:
            return

        try:
            episodios = self._modelo.obtenerEpisodios(pacienteVO.id_paciente)
            ep_actual = episodios[0] if episodios else None
            tratamientos = self._modelo.obtenerTratamientos_por_episodio(ep_actual.id_episodio) if ep_actual else []

            servicio = InformeAltaService()
            servicio.generar(
                ruta=ruta,
                pacienteVO=pacienteVO,
                episodios=episodios,
                tratamientos=tratamientos,
                medico_apellidos=self._user_vo.apellidos,
                diagnostico_alta=diagnostico_alta_reciente
            )

            self._vista.mostrar_notificacion(
                "Informe Generado",
                f"El informe clínico de alta se guardó de manera exitosa en:\n{ruta}"
            )
        except Exception as e:
            self._vista.mostrar_notificacion(
                "Error Interno",
                f"No se pudo estructurar el documento PDF:\n{str(e)}",
                es_error=True
            )

    def cargar_ingresos(self):
        ingresos = self._modelo.obtenerIngresosActuales()
        altas = self._modelo.obtenerAltasRecientes()
        self._ingresos_actuales = ingresos
        self._altas_recientes = altas
        self._vista.cargar_ingresos(ingresos if ingresos else [], altas if altas else [])

    # Llamado desde LogicaMedicos._buscar_en_ingresos()
    def filtrar_ingresos(self, texto):
        texto = texto.lower()
        ingresos_filtrados = [i for i in self._ingresos_actuales if texto in i.nombre_completo.lower()]
        altas = self._modelo.obtenerAltasRecientes() or []
        altas_filtradas = [a for a in altas if texto in a.nombre_completo.lower()]
        self._vista.cargar_ingresos(ingresos_filtrados, altas_filtradas)

    # CLASIFICACIÖN

    def clasificar_imagen(self, ruta):
        try:
            if self._logica_neumonia is None:
                self._logica_neumonia = LogicaNeumonia()  # se carga solo una vez

            resultados = self._logica_neumonia.clasificar(ruta)
            mejor = max(resultados, key=lambda r: r['score'])
            label = mejor['label']
            confianza = round(mejor['score'] * 100, 1)
            self._vista.mostrar_resultado(label, confianza)

        except Exception as e:
            self._vista.mostrar_error(str(e)) 