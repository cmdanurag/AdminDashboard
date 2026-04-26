import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings

async def send_mass_email(to_emails: list, subject: str, body: str):
    if not settings.SMTP_HOST or not settings.SMTP_USER:
        print(f"Mock email sent to {len(to_emails)} users. Subject: {subject}")
        return

    msg = MIMEMultipart()
    msg['From'] = settings.SMTP_USER
    msg['Subject'] = subject
    msg['Bcc'] = ", ".join(to_emails)
    
    msg.attach(MIMEText(body, 'html'))
    
    try:
        server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        print(f"Failed to send email: {e}")
