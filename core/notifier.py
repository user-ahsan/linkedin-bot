from core.logger import log_info, log_error
from config.config import CONFIG
# import smtplib
# from email.mime.text import MIMEText

class Notifier:
    def __init__(self):
        self.enabled = CONFIG["ENABLE_EMAIL_ALERTS"]
        
    def send_alert(self, subject, body):
        if not self.enabled:
            return
            
        log_info(f"Sending Email Alert: {subject}", module="NOTIFIER")
        # Logic to send email via SMTP would go here.
