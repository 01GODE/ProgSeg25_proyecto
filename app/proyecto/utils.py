import random
import os
import secrets
from django.core.mail import send_mail
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")


def generate_otp():
    return str(secrets.randbelow(900000) + 100000)

def send_otp_email(email, otp):
    send_mail(
        "Código OTP",
        f"Hola, tu código OTP es: {otp}.",
        EMAIL_HOST_USER,
        [email],
        fail_silently=False,
    )

LOG_DIR = os.path.join(os.path.dirname(__file__), '../logs')
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, 'bitacora.txt')

def escribir_bitacora(usuario, ip, accion):
    timestamp = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
    linea = f"[{timestamp}] {usuario or 'Anónimo'} - {ip} - {accion}\n"
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(linea)