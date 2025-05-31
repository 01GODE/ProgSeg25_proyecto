import MySQLdb
import os
from dotenv import load_dotenv
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.contrib.auth import logout

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_PORT = int(os.getenv("DB_PORT"))

def index(request):
    return render(request, 'index.html')

def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        # Conectar a MySQL
        try:
            db = MySQLdb.connect(host=DB_HOST, user=DB_USER, passwd=DB_PASSWORD, db=DB_NAME, port=DB_PORT)
            cursor = db.cursor()

            # Buscar el usuario en la base de datos
            cursor.execute("SELECT password FROM usuarios WHERE username=%s", [username])
            user_data = cursor.fetchone()
            db.close()

            # Validar credenciales
            if user_data and check_password(password, user_data[0]):
                request.session["usuario"] = username
                return redirect("inicio")  # Redirigir al inicio

        except MySQLdb.Error as e:
            print(f"Error de conexión a MySQL: {e}")
            return render(request, "index.html", {"error": "Error al conectar con la base de datos"})

        return render(request, "index.html", {"error": "Usuario o contraseña incorrectos"})

    return render(request, "index.html")

def inicio_view(request):
    usuario = request.session.get("usuario", "Invitado")
    return render(request, "inicio.html", {"usuario": usuario})

def logout_view(request):
    logout(request)  # Cierra la sesión del usuario
    request.session.flush()  # Elimina datos de sesión
    return redirect("index")  # Redirige al login