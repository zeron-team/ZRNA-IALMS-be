#backend/app/services/email_service.py

import smtplib
from email.mime.text import MIMEText
from app.config import EMAIL_HOST, EMAIL_PORT, EMAIL_USER, EMAIL_PASSWORD

def send_email(to_email: str, subject: str, body: str):
    if not all([EMAIL_HOST, EMAIL_PORT, EMAIL_USER, EMAIL_PASSWORD]):
        print("ERROR: Faltan variables de entorno para el envío de correos.")
        return

    msg = MIMEText(body, "html")
    msg['Subject'] = subject
    msg['From'] = EMAIL_USER
    msg['To'] = to_email

    try:
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.set_debuglevel(1) # <-- AÑADE ESTA LÍNEA DE DEPURACIÓN
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.send_message(msg)
        print(f"Correo enviado exitosamente a {to_email}")
    except Exception as e:
        print(f"Error detallado al enviar correo: {e}")

def send_verification_email(to_email: str, token: str):
    """Envía el correo para la verificación de la cuenta."""
    subject = "Verifica tu cuenta en IA LMS"
    verification_url = f"http://localhost:3000/verify-email?token={token}"
    body = f"""
    <h1>¡Bienvenido a IA LMS!</h1>
    <p>Gracias por registrarte. Por favor, haz clic en el siguiente enlace para activar tu cuenta:</p>
    <p><a href="{verification_url}" style="padding: 10px 15px; background-color: #3498db; color: white; text-decoration: none; border-radius: 5px;">Activar mi Cuenta</a></p>
    <p>Si no te registraste en nuestro sitio, puedes ignorar este correo.</p>
    """
    send_email(to_email, subject, body)

def send_password_reset_email(to_email: str, token: str):
    """Envía el correo para resetear la contraseña."""
    subject = "Restablecimiento de contraseña para IA LMS"
    reset_url = f"http://localhost:3000/reset-password?token={token}"
    body = f"""
    <h1>Restablecimiento de Contraseña</h1>
    <p>Has solicitado restablecer tu contraseña. Haz clic en el siguiente enlace para crear una nueva:</p>
    <p><a href="{reset_url}" style="padding: 10px 15px; background-color: #3498db; color: white; text-decoration: none; border-radius: 5px;">Crear Nueva Contraseña</a></p>
    <p>Si no solicitaste esto, puedes ignorar este correo de forma segura.</p>
    """
    send_email(to_email, subject, body)