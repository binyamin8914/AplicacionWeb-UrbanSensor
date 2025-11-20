from django.shortcuts import render
from django.conf import settings #importa el archivo settings
from django.contrib import messages #habilita la mesajería entre vistas
from django.contrib.auth.decorators import login_required #habilita el decorador que se niega el acceso a una función si no se esta logeado
from django.contrib.auth.models import Group, User # importa los models de usuarios y grupos
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator #permite la paqinación
from django.db.models import Avg, Count, Q #agrega funcionalidades de agregación a nuestros QuerySets
from django.http import (HttpResponse, HttpResponseBadRequest,
                         HttpResponseNotFound, HttpResponseRedirect) #Salidas alternativas al flujo de la aplicación se explicará mas adelante
from django.shortcuts import redirect, render #permite renderizar vistas basadas en funciones o redireccionar a otras funciones
from django.template import RequestContext # contexto del sistema
from django.views.decorators.csrf import csrf_exempt #decorador que nos permitira realizar conexiones csrf

from registration.models import Profile #importa el modelo profile, el que usaremos para los perfiles de usuarios
from incidencias.models import Incidencia
from direcciones.models import Direccion
from departamentos.models import Departamento
from cuadrillas.models import Cuadrilla


def home(request):
    return redirect('login')

@login_required
def pre_check_profile(request):
    #por ahora solo esta creada pero aún no la implementaremos
    pass

@login_required
def check_profile(request):  
    try:
        profile = Profile.objects.get(user=request.user)
    except:
        messages.add_message(request, messages.INFO, 'Hubo un error con su usuario, por favor contactese con los administradores')
        return redirect('login')
    # Para pruebas: deja pasar a cualquier usuario logueado
    return redirect('dashboard')

@login_required
def dashboard(request):  
    try:
        profile = Profile.objects.get(user=request.user)
        group_name = profile.group.name
    except:
        messages.add_message(request, messages.INFO, 'Hubo un error con su usuario, por favor contactese con los administradores')
        return redirect('login')
    
    data = {
        "datos": [],
        "group_name": group_name,
        "profile": profile,
    }

    if group_name == "SECPLA":
        n_usuarios = User.objects.count()
        #incidencias
        n_inc = Incidencia.objects.count()
        n_inc_abierta = Incidencia.objects.filter(estado="abierta").count()
        n_inc_derivadas = Incidencia.objects.filter(estado="derivada").count()
        n_inc_proceso = Incidencia.objects.filter(estado="proceso").count()
        n_inc_finalizada = Incidencia.objects.filter(estado="finalizada").count()
        n_inc_cerrada = Incidencia.objects.filter(estado="cerrada").count()
        n_inc_rechazada = Incidencia.objects.filter(estado="rechazada").count()
        # --- Carga por direccion (medido en el numero de incidencias) ---
        data["datos"] = [
            ("Total de usuarios", n_usuarios, ""),
            ("Total de incidencias", n_inc, "󱉫"),
            ("Incidencias abiertas", n_inc_abierta, ""),
            ("Incidencias derivadas", n_inc_derivadas, "󰏡"),
            ("Incidencias en proceso", n_inc_proceso, ""),
            ("Incidencias finalizadas", n_inc_finalizada, ""),
            ("Incidencias cerradas", n_inc_cerrada, "󰅚"),
            ("Incidencias rechazadas", n_inc_rechazada, "")
        ]
    elif group_name == "Direccion":
        direccion = Direccion.objects.get(encargado=request.user.id)
        #incidencias
        incidencias_direccion = Incidencia.objects.filter(encuesta__tipo_incidencia__departamento__direccion__id=direccion.id)
        n_inc = incidencias_direccion.count()
        n_inc_abierta = incidencias_direccion.filter(estado="abierta").count()
        n_inc_derivadas = incidencias_direccion.filter(estado="derivada").count()
        n_inc_proceso = incidencias_direccion.filter(estado="proceso").count()
        n_inc_finalizada = incidencias_direccion.filter(estado="finalizada").count()
        n_inc_cerrada = incidencias_direccion.filter(estado="cerrada").count()
        n_inc_rechazada = incidencias_direccion.filter(estado="rechazada").count()
        data["datos"] = [
            ("Total de incidencias", n_inc, "󱉫"),
            ("Incidencias abiertas", n_inc_abierta, ""),
            ("Incidencias derivadas", n_inc_derivadas, "󰏡"),
            ("Incidencias en proceso", n_inc_proceso, ""),
            ("Incidencias finalizadas", n_inc_finalizada, ""),
            ("Incidencias cerradas", n_inc_cerrada, "󰅚"),
            ("Incidencias rechazadas", n_inc_rechazada, "")
        ]
    elif group_name == "Departamento":
        departamento = Departamento.objects.get(encargado=request.user.id)
        #incidencias
        incidencias_departamento = Incidencia.objects.filter(encuesta__tipo_incidencia__departamento__id=departamento.id)
        n_inc = incidencias_departamento.count()
        n_inc_abierta = incidencias_departamento.filter(estado="abierta").count()
        n_inc_derivadas = incidencias_departamento.filter(estado="derivada").count()
        n_inc_proceso = incidencias_departamento.filter(estado="proceso").count()
        n_inc_finalizada = incidencias_departamento.filter(estado="finalizada").count()
        n_inc_cerrada = incidencias_departamento.filter(estado="cerrada").count()
        n_inc_rechazada = incidencias_departamento.filter(estado="rechazada").count()
        n_cuadrillas = Cuadrilla.objects.filter(departamento__id=departamento.id).count()
        data["datos"] = [
            ("Total de incidencias", n_inc, "󱉫"),
            ("Incidencias abiertas", n_inc_abierta, ""),
            ("Incidencias derivadas", n_inc_derivadas, "󰏡"),
            ("Incidencias en proceso", n_inc_proceso, ""),
            ("Incidencias finalizadas", n_inc_finalizada, ""),
            ("Incidencias cerradas", n_inc_cerrada, "󰅚"),
            ("Incidencias rechazadas", n_inc_rechazada, ""),
            ("Total de cuadrillas", n_cuadrillas, "")
        ]
    elif group_name == "Cuadrilla":
        #incidencias
        incidencias_cuadrilla = Incidencia.objects.filter(cuadrilla__id=request.user.id)
        n_inc = incidencias_cuadrilla.count()
        n_inc_abierta = incidencias_cuadrilla.filter(estado="abierta").count()
        n_inc_derivadas = incidencias_cuadrilla.filter(estado="derivada").count()
        n_inc_proceso = incidencias_cuadrilla.filter(estado="proceso").count()
        n_inc_finalizada = incidencias_cuadrilla.filter(estado="finalizada").count()
        n_inc_cerrada = incidencias_cuadrilla.filter(estado="cerrada").count()
        n_inc_rechazada = incidencias_cuadrilla.filter(estado="rechazada").count()
        data["datos"] = [
            ("Total de incidencias", n_inc, "󱉫"),
            ("Incidencias abiertas", n_inc_abierta, ""),
            ("Incidencias derivadas", n_inc_derivadas, "󰏡"),
            ("Incidencias en proceso", n_inc_proceso, ""),
            ("Incidencias finalizadas", n_inc_finalizada, ""),
            ("Incidencias cerradas", n_inc_cerrada, "󰅚"),
            ("Incidencias rechazadas", n_inc_rechazada, "")
        ]
    elif group_name == "Territorial":
        #incidencias
        incidencias_territorial = Incidencia.objects.filter(territorial__id=request.user.id)
        n_inc = incidencias_territorial.count()
        n_inc_abierta = incidencias_territorial.filter(estado="abierta").count()
        n_inc_derivadas = incidencias_territorial.filter(estado="derivada").count()
        n_inc_proceso = incidencias_territorial.filter(estado="proceso").count()
        n_inc_finalizada = incidencias_territorial.filter(estado="finalizada").count()
        n_inc_cerrada = incidencias_territorial.filter(estado="cerrada").count()
        n_inc_rechazada = incidencias_territorial.filter(estado="rechazada").count()
        data["datos"] = [
            ("Total de incidencias", n_inc, "󱉫"),
            ("Incidencias abiertas", n_inc_abierta, ""),
            ("Incidencias derivadas", n_inc_derivadas, "󰏡"),
            ("Incidencias en proceso", n_inc_proceso, ""),
            ("Incidencias finalizadas", n_inc_finalizada, ""),
            ("Incidencias cerradas", n_inc_cerrada, "󰅚"),
            ("Incidencias rechazadas", n_inc_rechazada, "")
        ]

    template_name = 'core/dashboard.html'
    return render(request, template_name, data)

def territorial_crear_incidencia(request):
    # Redirige a la vista real de crear incidencia que ya tienes en la app incidencias
    return redirect('crear_incidencia')
