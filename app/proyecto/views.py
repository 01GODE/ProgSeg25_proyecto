import MySQLdb
import os
import subprocess
from dotenv import load_dotenv
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import logout
from django.utils.timezone import now
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_http_methods
from proyecto.models import LoginAttempt , OTP
from proyecto.utils import generate_otp, send_otp_email, escribir_bitacora
from .forms import LoginCaptchaForm

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_PORT = int(os.getenv("DB_PORT"))

MAX_ATTEMPTS = 3
LOCK_TIME = 10


def index(request):
    """
    Vista inicial del sistema.

    Renderiza la página de inicio de sesión (`index.html`), sin realizar lógica adicional.
    """
    return render(request, 'index.html')


def get_client_ip(request):
    """
    Obtiene la dirección IP del cliente a partir de los encabezados de la solicitud.

    Si se encuentra detrás de un proxy, devuelve la primera IP en `X-Forwarded-For`.
    De lo contrario, se obtiene desde `REMOTE_ADDR`.
    """
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0]
    return request.META.get("REMOTE_ADDR")

@require_http_methods(["GET", "POST"])
def login_view(request):
    """
    Vista para gestionar el inicio de sesión con validación de captcha e intentos fallidos.

    - Si el formulario es válido y las credenciales coinciden, se genera y envía un código OTP por correo.
    - Si el usuario supera el número máximo de intentos fallidos dentro del intervalo bloqueado, se muestra un mensaje de espera.
    - En caso de error de autenticación, conexión con la base de datos o captcha inválido, se muestra el mensaje correspondiente.
    - Limpia la sesión al inicio para evitar conflictos de sesión anteriores.
    """
    request.session.flush()
    if request.method == "POST":
        form = LoginCaptchaForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            client_ip = get_client_ip(request)

            attempt, _ = LoginAttempt.objects.get_or_create(ip=client_ip, username=username)
            time_since_last = (now() - attempt.last_attempt).total_seconds()

            if attempt.attempts >= MAX_ATTEMPTS and time_since_last < LOCK_TIME:
                escribir_bitacora(username, client_ip, "Usuario bloqueado temporalmente")
                return render(request, "index.html", {
                    "form": form,
                    "error": f"Demasiados intentos. Intenta en 30 segundos, quedan: {LOCK_TIME - time_since_last:.0f} segundos."
                })

            try:
                db = MySQLdb.connect(host=DB_HOST, user=DB_USER, passwd=DB_PASSWORD, db=DB_NAME, port=DB_PORT)
                cursor = db.cursor()
                cursor.execute("SELECT id, password, correo FROM usuarios WHERE username=%s", [username])
                user_data = cursor.fetchone()
                db.close()

                if user_data and check_password(password, user_data[1]):
                    user_id, email = user_data[0], user_data[2]
                    request.session["usuario"] = username
                    request.session["user_id"] = user_id
                    attempt.attempts = 0
                    attempt.save()

                    otp_code = generate_otp()
                    otp_obj = OTP.objects.filter(user_id=user_id, is_used=False).first()
                    if otp_obj:
                        otp_obj.code = otp_code
                        otp_obj.created_at = now()
                        otp_obj.save()
                    else:
                        OTP.objects.create(user_id=user_id, code=otp_code, created_at=now(), is_used=False)

                    send_otp_email(email, otp_code)
                    request.session["otp_sent"] = True
                    return redirect("verificacion")

                attempt.attempts += 1
                attempt.save()
                escribir_bitacora(username, client_ip, "Intento fallido de inicio de sesión | Usuario o contraseña incorrectos.")
                return render(request, "index.html", {"form": form, "error": "Usuario o contraseña incorrectos."})

            except MySQLdb.Error:
                escribir_bitacora(username, client_ip, "Error al conectar con la base de datos")
                return render(request, "index.html", {"form": form, "error": "Error de conexión con la base de datos."})
        else:
            return render(request, "index.html", {"form": form, "error": "Captcha inválido."})
    else:
        form = LoginCaptchaForm()
    return render(request, "index.html", {"form": form})

@require_http_methods(["GET", "POST"])
def verificacion_view(request):
    """
    Vista para verificar el código OTP tras login.
    Si el código es válido, habilita acceso y redirige a 'inicio'.
    Si es inválido, redirige a 'index' con un mensaje de error.
    """
    usuario = request.session.get("usuario")
    user_id = request.session.get("user_id")
    client_ip = get_client_ip(request)

    if not usuario or not user_id:
        return redirect("index")

    if request.method == "POST":
        otp_code = request.POST.get("otp")
        otp = OTP.objects.filter(user_id=user_id, code=otp_code, is_used=False).first()

        if otp and not otp.is_expired():
            otp.is_used = True
            otp.save()
            request.session["authenticated"] = True
            escribir_bitacora(usuario, client_ip, " Inicio de sesión exitoso | OTP verificado con éxito")
            return redirect("inicio")
        else:
            escribir_bitacora(usuario, client_ip, "Intento fallido de inicio de sesión | Código OTP inválido o expirado")
            messages.error(request, "Código inválido")
            return redirect("index")

    return render(request, "verificacion.html")

@require_GET
def inicio_view(request):
    """
    Vista principal tras autenticación.

    Verifica sesión activa y OTP correcto. Redirige si la sesión no es válida.
    """
    usuario = request.session.get("usuario")  
    otp_verificado = request.session.get("authenticated")

    if not usuario or not otp_verificado:
        request.session.flush()
        return redirect("index")
    return render(request, "inicio.html", {"usuario": usuario})

@require_http_methods(["GET", "POST"])
def administrar_view(request):
    """
    Administra servicios remotos vía SSH con clave pública.

    - Lista servidores disponibles.
    - Carga servicios o ejecuta acción mediante conexión SSH.
    """

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
        cursor.execute("SELECT id, nombre, ip, usuario FROM servidores")
        servidores = cursor.fetchall()
        cursor.close()
        db.close()
    except MySQLdb.Error:
        messages.error(request, "No se pudo acceder a la base de datos.")

    if request.method == "POST":
        accion = request.POST.get("accion")
        servidor_id = request.POST.get("server-name")
        servidor = next((s for s in servidores if str(s["id"]) == servidor_id), None)

        if not servidor:
            messages.error(request, "Servidor inválido.")
            return redirect("administrar")

        if accion == "verificar":
            comando = (
                "systemctl list-units --type=service --all | "
                "grep -E 'active|inactive' | grep -v 'not-found' | "
                "awk '{ split($1, name, \".service\"); print name[1] }'"
            )
            try:
                resultado = subprocess.run(
                    ["ssh", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=no",
                     f"{servidor['usuario']}@{servidor['ip']}", comando],
                    capture_output=True, text=True, timeout=10
                )
                if resultado.returncode == 0:
                    servicios = resultado.stdout.strip().splitlines()
                    if not servicios:
                        messages.warning(request, "No se encontraron servicios en el servidor.")
                else:
                    messages.error(request, "Fallo al obtener servicios del servidor.")
            except Exception as e:
                messages.error(request, f"Error en la conexión SSH: {e}")

            return render(request, "administrar.html", {
                "usuario": usuario,
                "servidores": servidores,
                "servicios": servicios,
                "servidor_seleccionado": servidor_id
            })

        elif accion == "ejecutar":
            servicio = request.POST.get("service-name")
            opcion = request.POST.get("opcion")
            if not servicio or not opcion:
                messages.error(request, "Debe seleccionar un servicio y una acción.")
                return redirect("administrar")

            cmd = f"sudo systemctl {'restart' if opcion == 'Reiniciar' else 'stop'} {servicio}.service"
            try:
                resultado = subprocess.run(
                    ["ssh", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=no",
                     f"{servidor['usuario']}@{servidor['ip']}", cmd],
                    capture_output=True, text=True, timeout=10
                )
                if resultado.returncode == 0:
                    messages.success(request, f"{opcion} de '{servicio}' completada.")
                else:
                    messages.error(request, "Fallo al ejecutar la operación.")
            except Exception as e:
                messages.error(request, f"Error en la conexión SSH: {e}")

            return redirect("administrar")

    return render(request, "administrar.html", {
        "usuario": usuario,
        "servidores": servidores,
        "servicios": []
    })



@require_http_methods(["GET", "POST"])
def estado_view(request):
    """
    Vista que permite consultar el estado de servicios en un servidor remoto
    usando autenticación basada en clave SSH.

    - Verifica sesión y OTP.
    - Lista servidores desde la base de datos.
    - Usa el campo `usuario` e IP registrados para conectar sin contraseña.
    """

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
        cursor.execute("SELECT id, nombre, ip, usuario FROM servidores")
        servidores = cursor.fetchall()
        cursor.close()
        db.close()
    except MySQLdb.Error:
        messages.error(request, "Error al obtener la lista de servidores.")
        servidores = []

    if request.method == "POST":
        seleccion_id = request.POST.get("server-name")
        servidor_seleccionado = next((srv for srv in servidores if str(srv["id"]) == seleccion_id), None)

        if servidor_seleccionado:
            comando = (
                "systemctl list-units --type=service --all | "
                "grep -E 'active|inactive' | grep -v 'not-found' | "
                "awk '{ split($1, name, \".service\"); print name[1] \" \" $3 \" \" $4 }'"
            )

            try:
                resultado = subprocess.run(
                    ["ssh", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=no",
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
                                "actividad": partes[1].lower(),
                                "estado": partes[2].lower()
                            })
                else:
                    messages.error(request, "No se pudo obtener la lista de servicios del servidor.")
            except Exception as e:
                messages.error(request, f"Error en la conexión SSH: {e}")
        else:
            messages.error(request, "Servidor no encontrado.")

    return render(request, "estado.html", {
        "usuario": usuario,
        "servidores": servidores,
        "resultados": resultados,
        "servidor_seleccionado": servidor_seleccionado
    })


@require_GET
def actualizar_servicios(request):
    """
    Endpoint usado por AJAX para actualizar el estado de servicios de un servidor remoto.

    - Usa el ID del servidor para recuperar IP y usuario.
    - Conecta por SSH con clave pública y lista servicios.
    - Devuelve un JsonResponse con la información o errores.
    """
    server_id = request.GET.get("server_id")

    try:
        db = MySQLdb.connect(
            host=DB_HOST, user=DB_USER, passwd=DB_PASSWORD, db=DB_NAME, port=DB_PORT
        )
        cursor = db.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT id, nombre, ip, usuario FROM servidores")
        servidores = cursor.fetchall()
        cursor.close()
        db.close()
    except:
        return JsonResponse({"error": "Error de base de datos"}, status=500)

    servidor = next((s for s in servidores if str(s["id"]) == server_id), None)
    if not servidor:
        return JsonResponse({"error": "Servidor no encontrado"}, status=404)

    comando = (
        "systemctl list-units --type=service --all | "
        "grep -E 'active|inactive' | grep -v 'not-found' | "
        "awk '{ split($1, name, \".service\"); print name[1] \" \" $3 \" \" $4 }'"
    )

    try:
        resultado = subprocess.run(
            ["ssh", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=no",
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
        else:
            return JsonResponse({"error": "No se pudo obtener servicios"}, status=502)

        return JsonResponse({"servicios": servicios})
    except Exception as e:
        return JsonResponse({"error": f"Fallo SSH: {str(e)}"}, status=500)


@require_http_methods(["GET", "POST"])
def levantar_view(request):
    """
    Levanta un servicio remoto vía SSH usando clave pública.

    - Usa solo el nombre del servicio, usuario/IP ya registrados.
    - Requiere que sudo esté configurado sin contraseña para systemctl.
    """
    usuario = request.session.get("usuario")  
    otp_verificado = request.session.get("authenticated")

    if not usuario or not otp_verificado:
        request.session.flush()
        return redirect("index")

    servidores = []
    try:
        db = MySQLdb.connect(
            host=DB_HOST, user=DB_USER, passwd=DB_PASSWORD, db=DB_NAME, port=DB_PORT
        )
        cursor = db.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT id, nombre, ip, usuario FROM servidores")
        servidores = cursor.fetchall()
        cursor.close()
        db.close()
    except MySQLdb.Error:
        messages.error(request, "Error al obtener la lista de servidores.")
        servidores = []

    if request.method == "POST":
        servidor_id = request.POST.get("server-name")
        servicio_input = request.POST.get("nombre-servicio", "").strip()

        servidor = next((s for s in servidores if str(s["id"]) == servidor_id), None)

        if not servidor:
            messages.error(request, "Servidor inválido.")
            return redirect("levantar")

        if not servicio_input:
            messages.error(request, "Debe ingresar el nombre del servicio a levantar.")
            return redirect("levantar")

        comando = f"sudo systemctl start {servicio_input}.service"

        try:
            resultado = subprocess.run(
                ["ssh", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=no",
                 f"{servidor['usuario']}@{servidor['ip']}", comando],
                capture_output=True, text=True, timeout=10
            )

            if resultado.returncode == 0:
                messages.success(request, f"El servicio '{servicio_input}' se levantó correctamente.")
            else:
                stderr = resultado.stderr.strip()
                if "not found" in stderr or "Failed" in stderr:
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


@require_http_methods(["GET", "POST"])
def registro_view(request):
    """
    Vista que registra un nuevo servidor en la base de datos utilizando autenticación por clave SSH.

    - Verifica conectividad con el servidor (ping).
    - Intenta autenticación SSH sin contraseña.
    - Comprueba que el nombre/IP no estén ya registrados.
    - Guarda nombre, IP y usuario remoto.
    """
    usuario = request.session.get("usuario")  
    otp_verificado = request.session.get("authenticated")

    if not usuario or not otp_verificado:
        request.session.flush()
        return redirect("index")

    if request.method == "POST":
        nombre = request.POST.get("server-name", "").strip()
        ip = request.POST.get("ip-address", "").strip()
        usuario_ssh = request.POST.get("user", "").strip()

        if not nombre or not ip or not usuario_ssh:
            messages.error(request, "Todos los campos son obligatorios.")
            return redirect("registro")

        if subprocess.run(["ping", "-c", "1", ip], stdout=subprocess.DEVNULL).returncode != 0:
            messages.error(request, "No se encontró el servidor.")
            return redirect("registro")

        try:
            resultado = subprocess.run(
                ["ssh", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=no",
                 f"{usuario_ssh}@{ip}", "echo conectado"],
                capture_output=True, text=True, timeout=5
            )
            if "conectado" not in resultado.stdout:
                messages.error(request, "Conexión SSH fallida. Verifica si has instalado la clave pública.")
                return redirect("registro")
        except Exception as e:
            messages.error(request, f"No se pudo conectar por SSH: {str(e)}")
            return redirect("registro")

        try:
            db = MySQLdb.connect(
                host=DB_HOST, user=DB_USER, passwd=DB_PASSWORD, db=DB_NAME, port=DB_PORT
            )
            cursor = db.cursor()

            cursor.execute("SELECT id FROM servidores WHERE ip = %s", [ip])
            if cursor.fetchone():
                messages.error(request, "Servidor ya registrado con esa IP.")
                return redirect("registro")

            cursor.execute("SELECT id FROM servidores WHERE nombre = %s", [nombre])
            if cursor.fetchone():
                messages.error(request, "Ya existe un servidor con ese nombre.")
                return redirect("registro")

            cursor.execute("""
                INSERT INTO servidores (nombre, ip, usuario)
                VALUES (%s, %s, %s)
            """, (nombre, ip, usuario_ssh))

            db.commit()
            cursor.close()
            db.close()

            messages.success(request, "Servidor registrado correctamente.")
            return redirect("registro")

        except MySQLdb.Error:
            messages.error(request, "Error al guardar en la base de datos.")
            return redirect("registro")

    return render(request, "registro.html", {"usuario": usuario})


def logout_view(request):
    """
    Cierra la sesión del usuario y elimina los datos de la sesión activa.

    :return: Redirección a la vista de inicio de sesión ('index').
    """
    logout(request)
    request.session.flush()
    return redirect("index")