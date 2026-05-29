import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

gmail_user = os.getenv("GMAIL_USER")
gmail_app_password = os.getenv("GMAIL_APP_PASSWORD")
alert_to_email = os.getenv("ALERT_TO_EMAIL")

print("GMAIL_USER:", gmail_user)
print("ALERT_TO_EMAIL:", alert_to_email)

if not gmail_user or not gmail_app_password or not alert_to_email:
    raise ValueError("Missing Gmail values in .env file")

email = EmailMessage()
email["From"] = gmail_user
email["To"] = alert_to_email
email["Subject"] = "Test Alert from Stock Live Monitor"
email.set_content("Gmail setup is working. This is a test email from Python.")

with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
    smtp.login(gmail_user, gmail_app_password)
    smtp.send_message(email)

print("Test email sent successfully.")