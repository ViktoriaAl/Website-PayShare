import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

GMAIL_ADDRESS = os.environ.get("GMAIL_ADDRESS")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD")

def send_verification_email(to_email: str, verification_link: str):
    msg = MIMEMultipart("alternative")
    msg['Subject'] = "Подтвердите ваш email"
    msg['From'] = GMAIL_ADDRESS
    msg['To'] = to_email

    html_content = f"""
        <p>Здравствуйте! Чтобы продолжить регистацию, перейдите по ссылке:</p>
        <p><a herf="{verification_link}">{verification_link}</a></p>
        <p>Если вы не регестрировались на сайте PayShare, проигнорируйте это письмо.</p>
    """
    msg.attach(MIMEText(html_content, "html"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_ADDRESS, to_email, msg.as_string())
        return True
    except Exception as e:
        print(f"Email error {e}")
        return False
