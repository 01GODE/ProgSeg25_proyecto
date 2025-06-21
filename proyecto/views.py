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
    if not usuario:
        return redirect("index")

    servicios = []
    servidores = []
    servidor = None

    try:
        db = MySQLdb.connect(
            host=DB_HOST, user=DB_USER, passwd=DB_PASSWORD, db=DB_NAME, port=DB_PORT
        )
        cursor = db.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT id, nombre, ip, usuario, password_hash FROM servidores")
        servidores = cursor.fetchall()
        cursor.close()
        db.close()
    except MySQLdb.Error:
        messages.error(request, "No se pudo acceder a la base de datos.")

    if request.method == "POST":
        accion = request.POST.get("accion")
        servidor_id = request.POST.get("server-name")
        password_input = request.POST.get("pass_oculta", "").strip()
        servidor = next((s for s in servidores if str(s["id"]) == servidor_id), None)

        if not servidor:
            messages.error(request, "Servidor inválido.")
            return redirect("administrar")

        if not check_password(password_input, servidor["password_hash"]):
            messages.error(request, "Contraseña incorrecta.")
            return redirect("administrar")

        if accion == "verificar":
            comando = (
                f"echo '{password_input}' | sudo -S -p '' "
                "systemctl list-units --type=service --all | "
                "grep -E 'active|inactive' | grep -v 'not-found' | "
                "awk '{ split($1, name, \".service\"); print name[1] }'"
            )
            try:
                resultado = subprocess.run(
                    ["sshpass", "-p", password_input,
                     "ssh", "-o", "StrictHostKeyChecking=no",
                     f"{servidor['usuario']}@{servidor['ip']}",
                     comando],
                    capture_output=True, text=True, timeout=10
                )
                if resultado.returncode == 0:
                    servicios = resultado.stdout.strip().splitlines()
                    if not servicios:
                        messages.warning(request, "No se encontraron servicios en el servidor.")
                else:
                    messages.error(request, "Fallo al obtener servicios del servidor.")
            except Exception as e:
                print("EXCEPCIÓN:", str(e))
                messages.error(request, "Error en la conexión SSH.")

            # Muestra el formulario con servicios disponibles sin redirigir
            return render(request, "administrar.html", {
                "usuario": usuario,
                "servidores": servidores,
                "servicios": servicios,
                "servidor_seleccionado": servidor_id,
                "pass_oculta": password_input
            })

        elif accion == "ejecutar":
            servicio = request.POST.get("service-name")
            opcion = request.POST.get("opcion")
            if not servicio or not opcion:
                messages.error(request, "Debe seleccionar un servicio y una acción.")
                return redirect("administrar")

            cmd = f"systemctl {'restart' if opcion == 'Reiniciar' else 'stop'} {servicio}.service"
            comando = f"echo '{password_input}' | sudo -S -p '' {cmd}"
            try:
                resultado = subprocess.run(
                    ["sshpass", "-p", password_input,
                     "ssh", "-o", "StrictHostKeyChecking=no",
                     f"{servidor['usuario']}@{servidor['ip']}",
                     comando],
                    capture_output=True, text=True, timeout=10
                )
                if resultado.returncode == 0:
                    messages.success(request, f" {opcion.lower()} '{servicio}' Completado.")
                else:
                    messages.error(request, "Fallo al ejecutar la operación.")
            except Exception as e:
                print("EXCEPCIÓN:", str(e))
                messages.error(request, "Fallo en la conexión SSH.")

            return redirect("administrar")  # Solo redirigir después de ejecutar

    return render(request, "administrar.html", {
        "usuario": usuario,
        "servidores": servidores,
        "servicios": []
    })



def estado_view(request):
    usuario = request.session.get("usuario")
    otp_verificado = request.session.get("authenticated")

    if not usuario or not otp_verificado:
        return redirect("index")

    resultados = []
    servidor_seleccionado = None

    try:
        db = MySQLdb.connect(
            host=DB_HOST, user=DB_USER, passwd=DB_PASSWORD, db=DB_NAME, port=DB_PORT
        )
        cursor = db.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT id, nombre, ip, usuario, password_hash FROM servidores")
        servidores = cursor.fetchall()
        cursor.close()
        db.close()
    except MySQLdb.Error:
        messages.error(request, "Error al obtener la lista de servidores.")
        servidores = []

    if request.method == "POST":
        seleccion_id = request.POST.get("server-name")
        password_input = request.POST.get("pass_oculta", "").strip()

        servidor_seleccionado = next((srv for srv in servidores if str(srv["id"]) == seleccion_id), None)

        if servidor_seleccionado:
            hash_guardado = servidor_seleccionado["password_hash"]
            if not check_password(password_input, hash_guardado):
                messages.error(request, "La contraseña ingresada es incorrecta.")
                return redirect("estado")

            comando = (
                "systemctl list-units --type=service --all | "
                "grep -E 'active|inactive' | grep -v 'not-found' | "
                "awk '{ split($1, name, \".service\"); print name[1] \" \" $3 \" \" $4 }'"
            )

            try:
                resultado = subprocess.run(
                    ["sshpass", "-p", password_input,
                     "ssh", "-o", "StrictHostKeyChecking=no",
                     f"{servidor_seleccionado['usuario']}@{servidor_seleccionado['ip']}",
                     comando],
                    capture_output=True, text=True, timeout=10
                )

                if resultado.returncode == 0:
                    for linea in resultado.stdout.strip().splitlines():
                        partes = linea.strip().split()
                        if len(partes) == 3:
                            resultados.append({
                                "servicio": partes[0],
                                "actividad": partes[1].lower(),  # e.g. active/inactive
                                "estado": partes[2].lower()      # e.g. running/exited
                            })
                else:
                    messages.error(request, "No se pudo obtener la lista de servicios del servidor.")
            except Exception:
                messages.error(request, "Error al conectarse al servidor remoto.")
        else:
            messages.error(request, "Servidor no encontrado.")

    return render(request, "estado.html", {
        "usuario": usuario,
        "servidores": servidores,
        "resultados": resultados,
        "servidor_seleccionado": servidor_seleccionado
    })

def actualizar_servicios(request):
    server_id = request.GET.get("server_id")
    password = request.GET.get("password")

    # Replicamos validaciones y conexión
    try:
        db = MySQLdb.connect(
            host=DB_HOST, user=DB_USER, passwd=DB_PASSWORD, db=DB_NAME, port=DB_PORT
        )
        cursor = db.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT id, nombre, ip, usuario, password_hash FROM servidores")
        servidores = cursor.fetchall()
        cursor.close()
        db.close()
    except:
        return JsonResponse({"error": "Error de base de datos"}, status=500)

    servidor = next((s for s in servidores if str(s["id"]) == server_id), None)
    if not servidor or not check_password(password, servidor["password_hash"]):
        return JsonResponse({"error": "Acceso denegado"}, status=403)

    comando = (
        "systemctl list-units --type=service --all | "
        "grep -E 'active|inactive' | grep -v 'not-found' | "
        "awk '{ split($1, name, \".service\"); print name[1] \" \" $3 \" \" $4 }'"
    )

    try:
        resultado = subprocess.run(
            ["sshpass", "-p", password,
             "ssh", "-o", "StrictHostKeyChecking=no",
             f"{servidor['usuario']}@{servidor['ip']}", comando],
            capture_output=True, text=True, timeout=10
        )

        servicios = []
        if resultado.returncode == 0:
            for linea in resultado.stdout.strip().splitlines():
                partes = linea.split()
                if len(partes) == 3:
                    servicios.append({
                        "servicio": partes[0],
                        "actividad": partes[1].lower(),
                        "estado": partes[2].lower()
                    })
        return JsonResponse({"servicios": servicios})
    except:
        return JsonResponse({"error": "Fallo SSH"}, status=500)


def levantar_view(request):
    usuario = request.session.get("usuario")  
    otp_verificado = request.session.get("authenticated")

    # Si no hay sesión activa, redirigir al login
    if not usuario or not otp_verificado:
        request.session.flush()
        return redirect("index")

    servidores = []
    servidor = None

    try:
        db = MySQLdb.connect(
            host=DB_HOST, user=DB_USER, passwd=DB_PASSWORD, db=DB_NAME, port=DB_PORT
        )
        cursor = db.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT id, nombre, ip, usuario, password_hash FROM servidores")
        servidores = cursor.fetchall()
        cursor.close()
        db.close()
    except MySQLdb.Error:
        messages.error(request, "Error al obtener la lista de servidores.")

    if request.method == "POST":
        servidor_id = request.POST.get("server-name")
        password_input = request.POST.get("pass_oculta", "").strip()
        servicio_input = request.POST.get("nombre-servicio", "").strip()

        servidor = next((s for s in servidores if str(s["id"]) == servidor_id), None)

        if not servidor:
            messages.error(request, "Servidor inválido.")
            return redirect("levantar")

        if not check_password(password_input, servidor["password_hash"]):
            messages.error(request, "Contraseña incorrecta.")
            return redirect("levantar")

        if not servicio_input:
            messages.error(request, "Debe ingresar el nombre del servicio a levantar.")
            return redirect("levantar")

        comando = f"echo '{password_input}' | sudo -S -p '' systemctl start {servicio_input}.service"

        try:
            resultado = subprocess.run(
                ["sshpass", "-p", password_input,
                 "ssh", "-o", "StrictHostKeyChecking=no",
                 f"{servidor['usuario']}@{servidor['ip']}",
                 comando],
                capture_output=True, text=True, timeout=10
            )

            if resultado.returncode == 0:
                messages.success(request, f"El servicio '{servicio_input}' se levantó correctamente.")
            else:
                stderr = resultado.stderr.strip()
                if "not found" in stderr or "not be found" in stderr or "Failed" in stderr:
                    messages.error(request, f"El servicio '{servicio_input}' no existe o no se pudo levantar.")
                else:
                    messages.error(request, f"Error al intentar levantar el servicio: {stderr}")
        except Exception as e:
            messages.error(request, f"No se pudo conectar con el servidor: {str(e)}")

        return redirect("levantar")

    return render(request, "levantar.html", {
        "usuario": usuario,
        "servidores": servidores
    })



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
        password = request.POST.get("pass", "").strip()

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