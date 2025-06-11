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
from proyecto.models import OTP
from proyecto.utils import generate_otp, send_otp_email

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
    request.session.flush()  # Borra todos los datos de sesión al entrar al index
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        client_ip = get_client_ip(request)

        attempt, created = LoginAttempt.objects.get_or_create(ip=client_ip, username=username)

        time_since_last_attempt = (now() - attempt.last_attempt).total_seconds()
        if attempt.attempts >= MAX_ATTEMPTS and time_since_last_attempt < LOCK_TIME:
            return render(request, "index.html", {"error": f"Demasiados intentos. Intenta en 30 segundos, quedan: {LOCK_TIME - time_since_last_attempt:.0f} segundos."})

        try:
            db = MySQLdb.connect(host=DB_HOST, user=DB_USER, passwd=DB_PASSWORD, db=DB_NAME, port=DB_PORT)
            cursor = db.cursor()
            cursor.execute("SELECT id, password, correo FROM usuarios WHERE username=%s", [username])
            user_data = cursor.fetchone()
            db.close()

            if user_data and check_password(password, user_data[1]):
                user_id, email = user_data[0], user_data[2]  # Obtener ID y correo del usuario

                # Guardar usuario en sesión
                request.session["usuario"] = username
                request.session["user_id"] = user_id  # Guardamos el ID del usuario
                attempt.attempts = 0  
                attempt.save()

                # Generar y enviar el OTP automáticamente
                otp_code = generate_otp()
                OTP.objects.create(user_id=user_id, code=otp_code)
                send_otp_email(email, otp_code)  # Enviar el OTP al correo registrado
                request.session["otp_sent"] = True  

                # Redirigir a la página de verificación
                return redirect("verificacion")

            attempt.attempts += 1
            attempt.save()
            return render(request, "index.html", {"error": "Usuario o contraseña incorrectos."})

        except MySQLdb.Error:
            return render(request, "index.html", {"error": "Error al conectar con la base de datos."})

    return render(request, "index.html")

def verificacion_view(request):
    usuario = request.session.get("usuario")
    user_id = request.session.get("user_id")  

    if not usuario or not user_id:
        return redirect("index")

    if request.method == "POST":
        otp_code = request.POST.get("otp")

        # Verificar OTP ingresado
        otp = OTP.objects.filter(user_id=user_id, code=otp_code, is_used=False).first()

        if otp and not otp.is_expired():
            otp.is_used = True
            otp.save()
            request.session["authenticated"] = True  
            return redirect("inicio")
        return render(request, "verificacion.html", {"error": "El codigo es incorrecto"})
    
    return render(request, "verificacion.html")



def inicio_view(request):
    usuario = request.session.get("usuario")  
    otp_verificado = request.session.get("authenticated")
    
# Si no hay sesion de usuario, redirigir al login
    if not usuario or not otp_verificado:
        request.session.flush()  # Borra la sesión para mayor seguridad
        return redirect("index")
    return render(request, "inicio.html", {"usuario": usuario})

def estado_view(request):
    usuario = request.session.get("usuario")  
    otp_verificado = request.session.get("authenticated")

    # Si no hay sesion de usuario, redirigir al login
    if not usuario or not otp_verificado:
        request.session.flush()
        return redirect("index")
    
    return render(request, "estado.html", {"usuario": usuario})

def administrar_view(request):
    usuario = request.session.get("usuario")  
    otp_verificado = request.session.get("authenticated")

    # Si no hay sesion de usuario, redirigir al login
    if not usuario or not otp_verificado:
        request.session.flush()
        return redirect("index")
    
    return render(request, "administrar.html", {"usuario": usuario})

def levantar_view(request):
    usuario = request.session.get("usuario")  
    otp_verificado = request.session.get("authenticated")

    # Si no hay sesion de usuario, redirigir al login
    if not usuario or not otp_verificado:
        request.session.flush()
        return redirect("index")
    
    return render(request, "levantar.html", {"usuario": usuario})

def registro_view(request):
    usuario = request.session.get("usuario")  
    otp_verificado = request.session.get("authenticated")

    # Si no hay sesion de usuario, redirigir al login
    if not usuario or not otp_verificado:
        request.session.flush()
        return redirect("index")
    
    return render(request, "registro.html", {"usuario": usuario})

#cerra sesion
def logout_view(request):
    logout(request)  # Cierra la sesión del usuario
    request.session.flush()  # Elimina datos de sesión
    return redirect("index")  # Redirige al login