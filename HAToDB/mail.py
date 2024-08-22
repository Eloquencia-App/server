from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import config
import smtplib

class Mail:
    def __init__(self):
        self.server = smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT)
        self.server.starttls()
        self.server.login(config.SMTP_USER, config.SMTP_PASSWORD)

    def __del__(self):
        self.server.quit()

    def sendRegistrationMail(self, firstname, token, to):
        msg = MIMEMultipart()
        msg["From"] = config.SMTP_USER
        msg["To"] = to
        msg["Subject"] = "Finalisation de votre inscription chez Eloquéncia"
        body = f"Bonjour {firstname},\n\n" \
         f"Bienvenue chez Eloquéncia !\n\n" \
            f"Pour finaliser votre inscription, veuillez cliquer sur le lien suivant : http://localhost:5000/confirm?token={token}\n\n" \
            f"A bientôt !"
        msg.attach(MIMEText(body))

        self.server.sendmail(config.SMTP_USER, to, msg.as_string())