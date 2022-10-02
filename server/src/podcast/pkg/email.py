from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTP
from typing import List

from config.conf import ConfigFile


class EmailClient:
    def __init__(self):
        self.email_config = ConfigFile.get_email_config()
        self.server = None

    def __enter__(self):
        self.server = SMTP(self.email_config.get("smtp_host"), self.email_config.get("smtp_port"))
        if self.email_config.get("ssl") == "true":
            self.server.starttls()
        self.server.login(self.email_config.get("email"), self.email_config.get("password"))

        return self

    def __exit__(self, _, value, trace):
        self.server.quit()

    def send(self, to: List[str], subject: str, content: str):
        to.append(self.email_config.get("email"))
        message = MIMEMultipart('alternative')
        message['Subject'] = subject
        message['From'] = self.email_config.get("email")
        message['To'] = ','.join(to)

        message.attach(MIMEText(content, "html"))
        self.server.sendmail(message['From'], to, message.as_string())
