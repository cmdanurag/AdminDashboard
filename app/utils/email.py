import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings

async def send_mass_email(to_emails: list, subject: str, body: str):
    if not settings.SMTP_SERVER or not settings.SMTP_USERNAME:
        print(f"Mock email sent to {len(to_emails)} users. Subject: {subject}")
        return

    msg = MIMEMultipart()
    msg['From'] = settings.SMTP_USERNAME
    msg['Subject'] = subject
    msg['Bcc'] = ", ".join(to_emails)
    
    msg.attach(MIMEText(body, 'html'))
    
    try:
        server = smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT)
        server.starttls()
        server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        print(f"Failed to send email: {e}")
