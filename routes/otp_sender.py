
import base64
import smtplib
from email.mime.text import MIMEText
from pyotp import TOTP
import secrets


def send_otp_email(email, otp):
    # SMTP settings for Gmail
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    SMTP_USERNAME = "samarthasthan5@gmail.com"
    SMTP_PASSWORD = "rsllftyamztejfbe"
    SENDER_EMAIL = "samarthasthan5@gmail.com"


    # Generate an OTP using pyotp
    
    # random_secret_bytes = secrets.token_bytes(20)
    # otp_secret = base64.b32encode(random_secret_bytes).decode("utf-8")
    otp = TOTP(otp)
    one_time_password = otp.now()

    # Create the email content
    msg = MIMEText(f"Your OTP is: {one_time_password}")
    msg['Subject'] = 'OTP Verification'
    msg['From'] = SENDER_EMAIL
    msg['To'] = email

    # Send the email using SMTP
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(SENDER_EMAIL, [email], msg.as_string())

