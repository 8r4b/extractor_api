import os
from email.mime.text import MIMEText
import smtplib

def send_password_reset_email(email: str, token: str):
    link = f"http://localhost:8000/reset-password?token={token}"
    body = f"Click this link to reset your password:\n{link}"
    msg = MIMEText(body)
    msg["Subject"] = "Reset your password"
    msg["From"] = os.getenv("EMAIL_ADDRESS")
    msg["To"] = email
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(os.getenv("EMAIL_ADDRESS"), os.getenv("EMAIL_PASSWORD"))
            smtp.send_message(msg)
    except smtplib.SMTPException as e:
        print(f"SMTP error occurred: {e}")
    except Exception as e:
        print(f"Error sending password reset email: {e}")


def send_verification_email(email: str, token: str):
    link = f"http://localhost:8000/verify-email?token={token}"
    body = f"Click this link to verify your email:\n{link}"
    msg = MIMEText(body)
    msg["Subject"] = "Verify your email"
    msg["From"] = os.getenv("EMAIL_ADDRESS")
    msg["To"] = email
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(os.getenv("EMAIL_ADDRESS"), os.getenv("EMAIL_PASSWORD"))
            smtp.send_message(msg)
    except smtplib.SMTPException as e:
        print(f"SMTP error occurred: {e}")
    except Exception as e:
        print(f"Error sending verification email: {e}")
