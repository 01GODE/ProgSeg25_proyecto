import random
import os
from django.core.mail import send_mail
from dotenv import load_dotenv

load_dotenv()
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")

def generate_otp():
    #Genera un código OTP de 4 dígitos
    return str(random.randint(1000, 9999))

def send_otp_email(email, otp):
    send_mail(
        "Código OTP",
        f"Hola, tu código OTP es: {otp}.",
        EMAIL_HOST_USER,
        [email],
        fail_silently=False,
    )
