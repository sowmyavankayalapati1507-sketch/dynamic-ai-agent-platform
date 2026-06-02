import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

def send_email(to, subject, body):
    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = to

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)

        server.sendmail(
            EMAIL_ADDRESS,
            to,
            msg.as_string()
        )

        server.quit()

        return {
            "success": True,
            "message": f"Email sent to {to}"
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }