"""proyecto URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from proyecto.views import login_view, verificacion_view, inicio_view, logout_view, estado_view, administrar_view, levantar_view, registro_view, actualizar_servicios

urlpatterns = [
#    path('admin/', admin.site.urls),
	path("", login_view, name="index"),
    path("verificacion/", verificacion_view, name="verificacion"),
    path("inicio/", inicio_view, name="inicio"),
    path("logout/", logout_view, name="logout"),
    path("estado/", estado_view, name="estado"),  
    path("administrar/", administrar_view, name="administrar"),  
    path("levantar/", levantar_view, name="levantar"),  
    path("registro/", registro_view, name="registro"),
    path("actualizar_servicios/", actualizar_servicios, name="actualizar_servicios"),
]
