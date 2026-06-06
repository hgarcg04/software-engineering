
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QDateTime


from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, HRFlowable
from reportlab.lib import colors
from reportlab.lib.units import cm

class GeneradorInformePDF:

    def crear_pdf_informe(self, parent, ruta, pac):
        doc = SimpleDocTemplate(
            ruta,
            pagesize=A4,
            leftMargin=2 * cm,
            rightMargin=2 * cm,
            topMargin=2 * cm,
            bottomMargin=2 * cm
        )

        historia = []

        # --- CABECERA ---
        cabecera_data = [[
            Paragraph("Informe de Hospitalización"),
        ]]
        tabla_cabecera = Table(cabecera_data, colWidths=[17 * cm])

        historia.append(tabla_cabecera)
        historia.append(Spacer(1, 0.3 * cm))

        ahora = QDateTime.currentDateTime().toString("dd/MM/yyyy HH:mm")
        historia.append(Paragraph(f"Documento generado el {ahora}"))
        historia.append(Spacer(1, 0.5 * cm))

        # --- SECCIÓN: DATOS DEL PACIENTE ---
        historia.append(Paragraph("DATOS DEL PACIENTE"))
        historia.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#0cb868')))
        historia.append(Spacer(1, 0.2 * cm))

        datos_paciente = [
            [Paragraph("NIF / DNI:"), Paragraph(str(pac.nif)),
             Paragraph("Nombre completo:"), Paragraph(f"{pac.nombre} {pac.apellido1} {pac.apellido2}")],
            [Paragraph("Fecha de nacimiento:"), Paragraph(str(pac.fecha_nacimiento)),
             Paragraph("Género:"), Paragraph(str(pac.genero))],
        ]
        tabla_pac = Table(datos_paciente, colWidths=[4 * cm, 4.5 * cm, 4 * cm, 4.5 * cm])
        historia.append(tabla_pac)
        historia.append(Spacer(1, 0.5 * cm))

        # --- SECCIÓN: DATOS DEL INGRESO ---
        historia.append(Paragraph("DATOS DEL INGRESO"))
        historia.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#0cb868')))
        historia.append(Spacer(1, 0.2 * cm))

        fecha_ingreso = str(pac.fecha_inicio_ingreso)[:16] if pac.fecha_inicio_ingreso else "—"
        dieta = str(pac.dieta) if pac.dieta else "—"

        datos_ingreso = [
            [Paragraph("Habitación:"), Paragraph(str(pac.num_habitacion)),
             Paragraph("Fecha de ingreso:"), Paragraph(fecha_ingreso)],
            [Paragraph("Médico asignado:"), Paragraph(str(pac.medico_asignado)),
             Paragraph("Dieta:"), Paragraph(dieta)],
        ]
        tabla_ing = Table(datos_ingreso, colWidths=[4 * cm, 4.5 * cm, 4 * cm, 4.5 * cm])
        historia.append(tabla_ing)
        historia.append(Spacer(1, 1 * cm))

        # --- OBSERVACIONES ---

        historia.append(Paragraph("ANOTACIONES AL INGRESAR"))
        historia.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#0cb868")))
        historia.append(Spacer(1, 0.2 * cm))

        historia.append(Paragraph(str(pac.observaciones)))

        doc.build(historia)

        QMessageBox.information(parent, "PDF exportado", f"Informe guardado correctamente en:\n{ruta}")

