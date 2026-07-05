import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from src.core.logger import bookingseats_logger
from src.core.settings import settings


def send_email(
    body: str,
    recipient_email: str,
    subject: str = 'Уведомление системы бронирования',
) -> None:
    """Функция отправки сообщения."""
    with smtplib.SMTP(settings.smtp_server, settings.smtp_port) as server:
        server.starttls()
        server.login(settings.email_address, settings.email_password)

        # Создаем объект сообщения
        message = MIMEMultipart()
        message['From'] = settings.email_address
        message['To'] = recipient_email
        message['Subject'] = subject

        message.attach(MIMEText(body, 'plain'))

        server.sendmail(settings.email_address, recipient_email, message.as_string())
        bookingseats_logger.info(f'Email отправлен на {recipient_email}')
