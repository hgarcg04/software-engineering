from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, HRFlowable
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


class InformeAltaService:

    def generar(self, ruta, pacienteVO, episodios, tratamientos, medico_apellidos, diagnostico_alta):
        doc = SimpleDocTemplate(
            ruta, pagesize=A4,
            leftMargin=2*cm, rightMargin=2*cm,
            topMargin=2*cm, bottomMargin=2*cm
        )
        historia = []
        styles = getSampleStyleSheet()

        estilo_titulo = ParagraphStyle(
            'TituloSeccion_Alta', parent=styles['Heading2'],
            fontSize=12, textColor=colors.HexColor('#0cb868'),
            spaceBefore=12, spaceAfter=4
        )
        estilo_cabecera = ParagraphStyle(
            'Cabecera_Alta', parent=styles['Heading1'],
            fontSize=22, alignment=1,
            textColor=colors.HexColor('#2c3e50')
        )

        historia.append(Paragraph("<b>INFORME DE ALTA CLÍNICA</b>", estilo_cabecera))
        historia.append(Spacer(1, 0.3*cm))
        fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M")
        historia.append(Paragraph(f"<b>Documento emitido el:</b> {fecha_actual}", styles['Normal']))
        historia.append(Spacer(1, 0.6*cm))

        # Datos del paciente
        historia.append(Paragraph("<b>DATOS DEL PACIENTE</b>", estilo_titulo))
        historia.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0cb868')))
        historia.append(Spacer(1, 0.2*cm))
        datos_paciente = [
            [Paragraph("<b>NIF / DNI:</b>", styles['Normal']),
             Paragraph(str(pacienteVO.nif), styles['Normal']),
             Paragraph("<b>Paciente:</b>", styles['Normal']),
             Paragraph(f"{pacienteVO.nombre} {pacienteVO.apellido1} {pacienteVO.apellido2}", styles['Normal'])],
            [Paragraph("<b>F. Nacimiento:</b>", styles['Normal']),
             Paragraph(str(pacienteVO.fecha_nacimiento), styles['Normal']),
             Paragraph("<b>Género:</b>", styles['Normal']),
             Paragraph(str(pacienteVO.genero), styles['Normal'])],
        ]
        historia.append(Table(datos_paciente, colWidths=[3.5*cm, 5*cm, 3.5*cm, 5*cm]))
        historia.append(Spacer(1, 0.6*cm))

        # Detalles del episodio
        historia.append(Paragraph("<b>DETALLES DEL EPISODIO HOSPITALARIO</b>", estilo_titulo))
        historia.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0cb868')))
        historia.append(Spacer(1, 0.2*cm))
        ep_actual = episodios[0] if episodios else None
        if ep_actual:
            datos_ingreso = [
                [Paragraph("<b>ID Episodio:</b>", styles['Normal']),
                 Paragraph(str(ep_actual.id_episodio), styles['Normal']),
                 Paragraph("<b>Tipo de Ingreso:</b>", styles['Normal']),
                 Paragraph("Hospitalización en Planta", styles['Normal'])],
                [Paragraph("<b>Fecha de Inicio:</b>", styles['Normal']),
                 Paragraph(str(ep_actual.fecha_hora_inicio), styles['Normal']),
                 Paragraph("<b>Fecha de Alta:</b>", styles['Normal']),
                 Paragraph(datetime.now().strftime("%Y-%m-%d %H:%M"), styles['Normal'])],
                [Paragraph("<b>Médico Responsable:</b>", styles['Normal']),
                 Paragraph(f"Dr./Dra. {medico_apellidos}", styles['Normal']),
                 Paragraph("", styles['Normal']), Paragraph("", styles['Normal'])],
            ]
            historia.append(Table(datos_ingreso, colWidths=[3.5*cm, 5*cm, 3.5*cm, 5*cm]))
            historia.append(Spacer(1, 0.4*cm))
            historia.append(Paragraph("<b>DIAGNÓSTICO AL ALTA:</b>", styles['Normal']))
            historia.append(Spacer(1, 0.1*cm))
            texto_final = diagnostico_alta.replace('\n', '<br/>') if diagnostico_alta else "Sin diagnóstico especificado al alta."
            historia.append(Paragraph(texto_final, styles['Normal']))
        else:
            historia.append(Paragraph("No se registran detalles del episodio clínico activo.", styles['Normal']))

        # Plan de medicación
        historia.append(Paragraph("<b>PLAN DE MEDICACIÓN RECIENTE</b>", estilo_titulo))
        historia.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0cb868')))
        historia.append(Spacer(1, 0.3*cm))
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
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f8f9fa')),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
            ])
            historia.append(tabla_med)
        else:
            historia.append(Paragraph("El paciente no cuenta con tratamientos farmacológicos pautados para el hogar.", styles['Normal']))

        doc.build(historia)