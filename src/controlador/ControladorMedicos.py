from src.vista.Medicos.LogicaDialogoReceta import DialogoReceta
from src.vista.Medicos.LogicaDialogoEpisodio import DialogoEpisodio
from src.modelo.VO.EpisodiosVO import EpisodioVO
from src.modelo.VO.TratamientosVO import TratamientoVO
from src.controlador.ControladorNeumonia import ControladorNeumonia
from src.modelo.LogicaNeumonia import LogicaNeumonia

from datetime import datetime, timedelta

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, HRFlowable
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


class ControladorMedicos:
    def __init__(self, vista, modelo, user_vo, controlador_principal=None):
        self._vista = vista
        self._modelo = modelo
        self._user_vo = user_vo
        self.controlador_principal = controlador_principal

        self._episodios_actuales = []
        self._paciente_hcd_actual = None
        self._episodio_consulta_actual = None  # EpisodioVO activo en la consulta

        self._vista.cargar_datos_iniciales(self._user_vo)
        self._cargar_agenda_hoy()

        self._controlador_neumonia = ControladorNeumonia(vista, LogicaNeumonia())

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
        dialogo = DialogoReceta(parent=self._vista, cita_vo=cita)
        dialogo.lbl_pac_nombre.setText(cita.paciente_nombre)
        dialogo._id_paciente = cita.id_paciente
        dialogo._id_ingreso = cita.id_ingreso
        dialogo.controlador = self
        medicamentos = self._modelo.obtenerMedicamentos()
        dialogo.cargar_medicamentos(medicamentos)
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
        pacientes = self._modelo.buscarPacientePorId(id_paciente)
        if pacientes:
            self.cargar_episodios_paciente(pacientes[0])

    def dar_alta_paciente(self, diagnostico_alta):
        if not self._paciente_hcd_actual:
            self._vista.mostrar_notificacion(
                "Atención", 
                "No hay ningún paciente seleccionado para dar de alta.", 
                es_error=True
            )
            return
        episodios = self._modelo.obtenerEpisodios(self._paciente_hcd_actual.id_paciente)
        id_episodio = episodios[0].id_episodio if episodios else None

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

        # 1. Le pedimos a la vista que obtenga la ruta (El controlador no ve el QFileDialog)
        ruta = self._vista.solicitar_ruta_informe_alta(pacienteVO.nif)
        if not ruta:
            return  # El médico canceló la selección del archivo

        try:
            # 2. Configuración y maquetación del PDF (Lógica pura)
            doc = SimpleDocTemplate(
                ruta,
                pagesize=A4,
                leftMargin=2*cm,
                rightMargin=2*cm,
                topMargin=2*cm,
                bottomMargin=2*cm
            )

            historia = []
            styles = getSampleStyleSheet()

            # Estilo personalizado idéntico al de Enfermeros (Verde institucional)
            estilo_titulo_seccion = ParagraphStyle(
                'TituloSeccion_Alta',
                parent=styles['Heading2'],
                fontSize=12,
                textColor=colors.HexColor('#0cb868'),
                spaceBefore=12,
                spaceAfter=4
            )

            estilo_cabecera = ParagraphStyle(
                'Cabecera_Alta',
                parent=styles['Heading1'],
                fontSize=22,
                alignment=1,  # Centrado
                textColor=colors.HexColor('#2c3e50')
            )
            
            # --- DISEÑO DEL DOCUMENTO ---
            historia.append(Paragraph("<b>INFORME DE ALTA CLÍNICA</b>", estilo_cabecera))
            historia.append(Spacer(1, 0.3 * cm))
            
            fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M")
            historia.append(Paragraph(f"<b>Documento emitido el:</b> {fecha_actual}", styles['Normal']))
            historia.append(Spacer(1, 0.6 * cm))

            # SECCIÓN 1: DATOS DEL PACIENTE
            historia.append(Paragraph("<b>DATOS DEL PACIENTE</b>", estilo_titulo_seccion))
            historia.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0cb868')))
            historia.append(Spacer(1, 0.2 * cm))

            datos_paciente = [
                [Paragraph("<b>NIF / DNI:</b>", styles['Normal']), Paragraph(str(pacienteVO.nif), styles['Normal']),
                 Paragraph("<b>Paciente:</b>", styles['Normal']), Paragraph(f"{pacienteVO.nombre} {pacienteVO.apellido1} {pacienteVO.apellido2}", styles['Normal'])],
                [Paragraph("<b>F. Nacimiento:</b>", styles['Normal']), Paragraph(str(pacienteVO.fecha_nacimiento), styles['Normal']),
                 Paragraph("<b>Género:</b>", styles['Normal']), Paragraph(str(pacienteVO.genero), styles['Normal'])],
            ]
            tabla_pac = Table(datos_paciente, colWidths=[3.5*cm, 5*cm, 3.5*cm, 5*cm])
            historia.append(tabla_pac)
            historia.append(Spacer(1, 0.6 * cm))

            # SECCIÓN 2: DETALLES DEL EPISODIO
            historia.append(Paragraph("<b>DETALLES DEL EPISODIO HOSPITALARIO</b>", estilo_titulo_seccion))
            historia.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0cb868')))
            historia.append(Spacer(1, 0.2 * cm))

            episodios = self._modelo.obtenerEpisodios(pacienteVO.id_paciente)
            ep_actual = episodios[0] if episodios else None

            if ep_actual:
                # 🛠️ SOLUCIÓN: Forzamos que ponga "Hospitalización en Planta" en lugar de "Consulta"
                tipo_ingreso_bonito = "Hospitalización en Planta" 
                
                datos_ingreso = [
                    [Paragraph("<b>ID Episodio:</b>", styles['Normal']), Paragraph(str(ep_actual.id_episodio), styles['Normal']),
                     Paragraph("<b>Tipo de Ingreso:</b>", styles['Normal']), Paragraph(tipo_ingreso_bonito, styles['Normal'])],
                    [Paragraph("<b>Fecha de Inicio:</b>", styles['Normal']), Paragraph(str(ep_actual.fecha_hora_inicio), styles['Normal']),
                     Paragraph("<b>Fecha de Alta:</b>", styles['Normal']), Paragraph(datetime.now().strftime("%Y-%m-%d %H:%M"), styles['Normal'])],
                    [Paragraph("<b>Médico Responsable:</b>", styles['Normal']), Paragraph(f"Dr./Dra. {self._user_vo.apellidos}", styles['Normal']),
                     Paragraph("", styles['Normal']), Paragraph("", styles['Normal'])],
                ]
                tabla_ing = Table(datos_ingreso, colWidths=[3.5*cm, 5*cm, 3.5*cm, 5*cm])
                historia.append(tabla_ing)
                historia.append(Spacer(1, 0.4 * cm))
                
                historia.append(Paragraph("<b>DIAGNÓSTICO AL ALTA:</b>", styles['Normal']))
                historia.append(Spacer(1, 0.1 * cm))
                
                # 🛠️ SOLUCIÓN: Usamos el texto fresco que acaba de escribir el médico en la ventana
                texto_final = diagnostico_alta_reciente.replace('\n', '<br/>') if diagnostico_alta_reciente else "Sin diagnóstico especificado al alta."
                historia.append(Paragraph(texto_final, styles['Normal']))
            else:
                historia.append(Paragraph("No se registran detalles del episodio clínico activo.", styles['Normal']))

            # SECCIÓN 3: TRATAMIENTO RECOMENDADO
            historia.append(Paragraph("<b>PLAN DE MEDICACIÓN RECIENTE</b>", estilo_titulo_seccion))
            historia.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0cb868')))
            historia.append(Spacer(1, 0.3 * cm))

            tratamientos = self._modelo.obtenerTratamientos_por_episodio(ep_actual.id_episodio) if ep_actual else []

            if tratamientos:
                tabla_med_data = [[
                    Paragraph("<b>Medicamento</b>", styles['Normal']),
                    Paragraph("<b>Dosis</b>", styles['Normal']),
                    Paragraph("<b>Frecuencia</b>", styles['Normal']),
                    Paragraph("<b>Vía</b>", styles['Normal']),
                    Paragraph("<b>Instrucciones Facultativas</b>", styles['Normal'])
                ]]
                
                for t in tratamientos:
                    tabla_med_data.append([
                        Paragraph(str(t.get('medicamento', '—')), styles['Normal']),
                        Paragraph(str(t.get('dosis', '—')), styles['Normal']),
                        Paragraph(str(t.get('frecuencia', '—')), styles['Normal']),
                        Paragraph(str(t.get('via', '—')), styles['Normal']),
                        Paragraph(str(t.get('notas', '—')), styles['Normal'])
                    ])
                
                tabla_med = Table(tabla_med_data, colWidths=[3.5*cm, 2*cm, 3*cm, 2.5*cm, 6*cm])
                tabla_med.setStyle([
                    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f8f9fa')),
                    ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
                    ('VALIGN', (0,0), (-1,-1), 'TOP'),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 5),
                    ('TOPPADDING', (0,0), (-1,-1), 5),
                ])
                historia.append(tabla_med)
            else:
                historia.append(Paragraph("El paciente no cuenta con tratamientos farmacológicos pautados para el hogar.", styles['Normal']))

            doc.build(historia)
            
            self._vista.mostrar_notificacion(
                "Informe Generado", 
                f"El informe clínico de alta se guardó de manera exitosa en:\n{ruta}"
            )

        except Exception as e:
            print("Error generando PDF:", e)
            self._vista.mostrar_notificacion(
                "Error Interno", 
                f"No se pudo estructurar el documento PDF:\n{str(e)}", 
                es_error=True
            )

    def cargar_ingresos(self):
        ingresos = self._modelo.obtenerIngresosActuales()
        altas = self._modelo.obtenerAltasRecientes()
        self._vista.cargar_ingresos(ingresos if ingresos else [], altas if altas else [])

    # CLASIFICACIÖN

    def clasificar_imagen(self, ruta):
        self._controlador_neumonia.clasificar_imagen(ruta)  