import MySQLdb
import os
import re
import datetime
from dotenv import load_dotenv
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.contrib.auth import logout
from django.utils.timezone import now
from proyecto.models import LoginAttempt

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_PORT = int(os.getenv("DB_PORT"))

#intentos de login
MAX_ATTEMPTS = 3
LOCK_TIME = 10

def index(request):
    return render(request, 'index.html')

def get_client_ip(request):
    """Obtener la IP del usuario"""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0]
    return request.META.get("REMOTE_ADDR")

def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        client_ip = get_client_ip(request)

        # Buscar intentos previos del usuario
        attempt, created = LoginAttempt.objects.get_or_create(ip=client_ip, username=username)

        # Verificar si está bloqueado
        time_since_last_attempt = (now() - attempt.last_attempt).total_seconds()
        if attempt.attempts >= MAX_ATTEMPTS and time_since_last_attempt < LOCK_TIME:
            return render(request, "index.html", {"error": f"Demasiados intentos. Intenta en 30 segundos, quedan: {LOCK_TIME - time_since_last_attempt:.0f} segundos."})

        # Conectar a MySQL
        try:
            db = MySQLdb.connect(host=DB_HOST, user=DB_USER, passwd=DB_PASSWORD, db=DB_NAME, port=DB_PORT)
            cursor = db.cursor()
            cursor.execute("SELECT password FROM usuarios WHERE username=%s", [username])
            user_data = cursor.fetchone()
            db.close()

            # validar credenciales
            if user_data and check_password(password, user_data[0]):
                request.session["usuario"] = username
                attempt.attempts = 0  # Resetear intentos al iniciar sesión correctamente
                attempt.save()
                return redirect("inicio")

            attempt.attempts += 1  # Aumentar intentos fallidos
            attempt.save()
            return render(request, "index.html", {"error": "Usuario o contraseña incorrectos."})

        except MySQLdb.Error as e:
            return render(request, "index.html", {"error": "Error al conectar con la base de datos"})

    return render(request, "index.html")


def inicio_view(request):
    usuario = request.session.get("usuario")  
    # Si no hay sesion de usuario, redirigir al login
    if not usuario:
        return redirect("index")
    return render(request, "inicio.html", {"usuario": usuario})

#cerra sesion
def logout_view(request):
    logout(request)  # Cierra la sesión del usuario
    request.session.flush()  # Elimina datos de sesión
    return redirect("index")  # Redirige al login