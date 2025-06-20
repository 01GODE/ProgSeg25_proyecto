import MySQLdb
import os
import re
import datetime
import subprocess
from dotenv import load_dotenv
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.contrib.auth import logout
from django.utils.timezone import now
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
import MySQLdb
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

                # Generar un nuevo OTP
                otp_code = generate_otp()

                # Buscar si el usuario ya tiene un OTP sin usar
                otp_existente = OTP.objects.filter(user_id=user_id, is_used=False).first()

                if otp_existente:
                    # Si ya hay un código previo, actualizarlo
                    otp_existente.code = otp_code
                    otp_existente.created_at = now()  # Actualizar fecha de creación
                    otp_existente.save()
                else:
                    # Si no existe un código previo, crear uno nuevo
                    OTP.objects.create(user_id=user_id, code=otp_code, created_at=now(), is_used=False)

                # Enviar el código OTP al correo del usuario
                send_otp_email(email, otp_code)
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


def administrar_view(request):
    usuario = request.session.get("usuario")  
    otp_verificado = request.session.get("authenticated")

    # Si no hay sesion de usuario, redirigir al login
    if not usuario or not otp_verificado:
        request.session.flush()
        return redirect("index")
    
    return render(request, "estado.html", {"usuario": usuario})


def estado_view(request):
    usuario = request.session.get("usuario")
    otp_verificado = request.session.get("authenticated")

    if not usuario or not otp_verificado:
        request.session.flush()
        return redirect("index")

    servidores = []
    resultados = None
    servidor_seleccionado = None

    # Cargar servidores desde la base de datos
    try:
        db = MySQLdb.connect(
            host=DB_HOST, user=DB_USER, passwd=DB_PASSWORD, db=DB_NAME, port=DB_PORT
        )
        cursor = db.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT nombre, ip, usuario, password_hash FROM servidores")
        servidores = cursor.fetchall()
        cursor.close()
        db.close()
    except MySQLdb.Error:
        messages.error(request, "Error al obtener la lista de servidores.")

    if request.method == "POST":
        seleccion = request.POST.get("server-name")
        password_input = request.POST.get("pass_oculta", "").strip()
        servidor_seleccionado = next((srv for srv in servidores if srv["nombre"] == seleccion), None)

        if servidor_seleccionado:
            hash_guardado = servidor_seleccionado["password_hash"]

            if not check_password(password_input, hash_guardado):
                messages.error(request, "La contraseña ingresada no coincide con la registrada.")
                return redirect("estado")

            try:
                comando = (
                    "systemctl list-unit-files --type=service | "
                    "grep -E 'enabled|disabled' | grep -vE 'masked|static' | "
                    "awk '{gsub(/\\.service$/, \"\", $1); print $1 \" → \" $2}'"
                )

                resultado = subprocess.run(
                    ["sshpass", "-p", password_input,
                     "ssh", "-o", "StrictHostKeyChecking=no",
                     f"{servidor_seleccionado['usuario']}@{servidor_seleccionado['ip']}",
                     comando],
                    capture_output=True, text=True, timeout=7
                )

                if resultado.returncode == 0:
                    resultados = []
                    for linea in resultado.stdout.strip().splitlines():
                            if " → " in linea:
                                servicio, estado = linea.split(" → ")
                            resultados.append({"servicio": servicio, "estado": estado})

                else:
                    messages.error(request, "Error al obtener servicios del servidor.")
            except Exception:
                messages.error(request, "No se pudo conectar al servidor.")

    return render(request, "estado.html", {"usuario": usuario, "servidores": servidores, "resultados": resultados, "servidor_seleccionado": servidor_seleccionado
    })


def estado_dinamico(request):
    if request.method == "GET" and request.is_ajax():
        nombre_servidor = request.GET.get("nombre")
        password_input = request.GET.get("password")

        try:
            db = MySQLdb.connect(
                host=DB_HOST, user=DB_USER, passwd=DB_PASSWORD, db=DB_NAME, port=DB_PORT
            )
            cursor = db.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT nombre, ip, usuario, password_hash FROM servidores WHERE nombre = %s", [nombre_servidor])
            srv = cursor.fetchone()
            cursor.close()
            db.close()
        except Exception:
            return JsonResponse({"error": "Error de base de datos."}, status=500)

        if not srv or not check_password(password_input, srv["password_hash"]):
            return JsonResponse({"error": "Autenticación fallida."}, status=403)

        comando = (
            "systemctl list-unit-files --type=service | grep -E 'enabled|disabled' "
            "| grep -vE 'masked|static' | awk '{gsub(/\\.service$/, \"\", $1); print $1 \"|\" $2}'"
        )
        try:
            resultado = subprocess.run(
                ["sshpass", "-p", password_input,
                 "ssh", "-o", "StrictHostKeyChecking=no",
                 f"{srv['usuario']}@{srv['ip']}",
                 comando],
                capture_output=True, text=True, timeout=7
            )
            servicios = []
            for linea in resultado.stdout.strip().splitlines():
                if "|" in linea:
                    nombre, estado = linea.strip().split("|")
                    servicios.append({"nombre": nombre, "estado": estado})
            return JsonResponse({"servicios": servicios})
        except Exception:
            return JsonResponse({"error": "Error de conexión SSH."}, status=500)


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

    if not usuario or not otp_verificado:
        request.session.flush()
        return redirect("index")

    if request.method == "POST":
        nombre = request.POST["server-name"]
        ip = request.POST["ip-address"]
        usuario_ssh = request.POST["user"]
        password = request.POST["pass"]

        # 1. Verificar conectividad con ping (desde el servidor Django)
        if subprocess.run(["ping", "-c", "1", ip], stdout=subprocess.DEVNULL).returncode != 0:
            messages.error(request, "No se encontró el servidor")
            return redirect("registro")

        # 2. Verificar credenciales SSH
        try:
            test = subprocess.run(
                ["sshpass", "-p", password,
                 "ssh", "-o", "StrictHostKeyChecking=no",
                 f"{usuario_ssh}@{ip}", "echo conectado"],
                capture_output=True, text=True, timeout=5
            )
            if "conectado" not in test.stdout:
                messages.error(request, "Usuario o contraseña incorrectos")
                return redirect("registro")
        except Exception:
            messages.error(request, "Error al conectar por SSH")
            return redirect("registro")

        # 3. Conectarse a MySQL
        try:
            db = MySQLdb.connect(
                host=DB_HOST, user=DB_USER, passwd=DB_PASSWORD, db=DB_NAME, port=DB_PORT
            )
            cursor = db.cursor()

            # 4. Verificar si la IP ya está registrada
            cursor.execute("SELECT id FROM servidores WHERE ip = %s", [ip])
            if cursor.fetchone():
                messages.error(request, "Servidor ya registrado con esa IP")
                return redirect("registro")

            # 4.1 Verificar si el nombre ya está registrado
            cursor.execute("SELECT id FROM servidores WHERE nombre = %s", [nombre])
            if cursor.fetchone():
                messages.error(request, "Ya existe un servidor con ese nombre")
                return redirect("registro")

            # 5. Hashear contraseña con salt interno de Django
            password_hash = make_password(password)

            # 6. Insertar en la base de datos
            cursor.execute("""
                INSERT INTO servidores (nombre, ip, usuario, password_hash)
                VALUES (%s, %s, %s, %s)
            """, (nombre, ip, usuario_ssh, password_hash))
            db.commit()
            cursor.close()
            db.close()

            messages.success(request, "Servidor registrado correctamente")
            return redirect("registro")

        except MySQLdb.Error:
            messages.error(request, "Error al guardar en la base de datos")
            return redirect("registro")

    return render(request, "registro.html", {"usuario": usuario})


#cerra sesion
def logout_view(request):
    logout(request)  # Cierra la sesión del usuario
    request.session.flush()  # Elimina datos de sesión
    return redirect("index")  # Redirige al login