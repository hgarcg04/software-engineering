import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class EmailService:
    """
    Servicio de notificación por email.
    Ubicación: src/modelo/servicios/EmailService.py

    Responsabilidad única: construir y enviar emails transaccionales.
    No accede a la BD ni conoce la vista; es invocado exclusivamente desde Logica.py.
    """

    REMITENTE  = "hospital.tkura@gmail.com"       # ← sustituir por la cuenta creada
    CLAVE      = "jsnm rmap rqia tdns"      # ← clave de aplicación de 16 caracteres
    SMTP_HOST  = "smtp.gmail.com"
    SMTP_PORT  = 587

    def enviar_confirmacion_cita(self, correo_paciente, nombre_paciente,
                                  nombre_medico, fecha, hora):
        """
        Envía un email de confirmación al paciente tras asignarle una cita.

        Parámetros
        ----------
        correo_paciente : str
        nombre_paciente : str   — nombre completo del paciente
        nombre_medico   : str   — nombre completo del médico
        fecha           : str   — 'YYYY-MM-DD'
        hora            : str   — 'HH:MM'
        """
        if not correo_paciente or not correo_paciente.strip():
            print("EmailService: el paciente no tiene correo registrado, se omite el envío.")
            return

        try:
            msg = MIMEMultipart()
            msg["From"]    = self.REMITENTE
            msg["To"]      = correo_paciente
            msg["Subject"] = "Confirmación de cita médica — KURA"

            cuerpo = (
                f"Estimado/a {nombre_paciente},\n\n"
                f"Le confirmamos que su cita ha sido asignada correctamente.\n\n"
                f"  Médico : {nombre_medico}\n"
                f"  Fecha  : {fecha}\n"
                f"  Hora   : {hora}\n\n"
                f"Por favor, preséntese con 10 minutos de antelación.\n\n"
                f"Atentamente,\n"
                f"Equipo KURA"
            )
            msg.attach(MIMEText(cuerpo, "plain", "utf-8"))

            with smtplib.SMTP(self.SMTP_HOST, self.SMTP_PORT) as servidor:
                servidor.starttls()
                servidor.login(self.REMITENTE, self.CLAVE)
                servidor.sendmail(self.REMITENTE, correo_paciente, msg.as_string())

            print(f"EmailService: confirmación enviada a {correo_paciente}")

        except smtplib.SMTPAuthenticationError:
            print("EmailService: error de autenticación. Comprueba el correo y la clave de aplicación.")
        except smtplib.SMTPException as e:
            print(f"EmailService: error SMTP al enviar a {correo_paciente}: {e}")
        except Exception as e:
            print(f"EmailService: error inesperado: {e}")