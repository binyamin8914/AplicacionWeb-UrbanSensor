from django.shortcuts import render
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, User
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Prefetch, Avg, Count, Q
from django.http import (HttpResponse, HttpResponseBadRequest,
                         HttpResponseNotFound, HttpResponseRedirect)
from django.shortcuts import redirect, render
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt

from registration.models import Profile
from incidencias.models import Incidencia
from direcciones.models import Direccion
from departamentos.models import Departamento
from cuadrillas.models import Cuadrilla

from django.utils.timezone import localtime


def home(request):
    return redirect('login')

@login_required
def pre_check_profile(request):
    pass

@login_required
def check_profile(request):  
    try:
        profile = Profile.objects.get(user=request.user)
    except:
        messages.add_message(request, messages.INFO, 'Hubo un error con su usuario, por favor contactese con los administradores')
        return redirect('login')
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
        n_inc = Incidencia.objects.count()
        n_inc_abierta = Incidencia.objects.filter(estado="abierta").count()
        n_inc_derivadas = Incidencia.objects.filter(estado="derivada").count()
        n_inc_proceso = Incidencia.objects.filter(estado="proceso").count()
        n_inc_finalizada = Incidencia.objects.filter(estado="finalizada").count()
        n_inc_cerrada = Incidencia.objects.filter(estado="cerrada").count()
        n_inc_rechazada = Incidencia.objects.filter(estado="rechazada").count()

        historial_incidencias = Incidencia.objects.order_by('-updated_at').values('encuesta__titulo', 'prioridad', 'estado', 'updated_at')[:5]
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
        data['historial_incidencias'] = list(historial_incidencias)

    elif group_name == "Direccion":
        direccion = Direccion.objects.get(encargado=request.user.id)
        departamentos = Departamento.objects.filter(direccion__id=direccion.id)
        n_dep = departamentos.count()
        incidencias_direccion = Incidencia.objects.filter(encuesta__tipo_incidencia__departamento__direccion__id=direccion.id)
        list_incidencias = list(incidencias_direccion.values('encuesta__tipo_incidencia__departamento__nombre', 'estado'))
        departamento_incidencias = {}
        max_total = 0

        for incidencia in list_incidencias:
            nombre = incidencia['encuesta__tipo_incidencia__departamento__nombre']
            estado = incidencia['estado']
            if nombre not in departamento_incidencias:
                departamento_incidencias[nombre] = {
                    'nombre_dep': nombre,
                    'n_inc': 0,
                    'n_inc_abierta': 0,
                    'n_inc_derivada': 0,
                    'n_inc_proceso': 0,
                    'n_inc_finalizada': 0,
                    'n_inc_cerrada': 0,
                    'n_inc_rechazada': 0
                }
            departamento_incidencias[nombre]['n_inc'] = departamento_incidencias[nombre]['n_inc'] + 1
            if estado == 'abierta':
                departamento_incidencias[nombre]['n_inc_abierta'] = departamento_incidencias[nombre]['n_inc_abierta'] + 1
            if estado == 'derivada':
                departamento_incidencias[nombre]['n_inc_derivada'] = departamento_incidencias[nombre]['n_inc_derivada'] + 1
            if estado == 'proceso':
                departamento_incidencias[nombre]['n_inc_proceso'] = departamento_incidencias[nombre]['n_inc_proceso'] + 1
            if estado == 'finalizada':
                departamento_incidencias[nombre]['n_inc_finalizada'] = departamento_incidencias[nombre]['n_inc_finalizada'] + 1
            if estado == 'cerrada':
                departamento_incidencias[nombre]['n_inc_cerrada'] = departamento_incidencias[nombre]['n_inc_cerrada'] + 1
            if estado == 'rechazada':
                departamento_incidencias[nombre]['n_inc_rechazada'] = departamento_incidencias[nombre]['n_inc_rechazada'] + 1
        
        departamento_incidencias = list(departamento_incidencias.values())

        for dep in departamento_incidencias:
            if max_total < dep['n_inc']:
                max_total = dep['n_inc']


        n_inc = incidencias_direccion.count()
        data["datos"] = [
            ("Total de incidencias", n_inc, "󱉫"),
            ("Departamentos", n_dep, "ic")
        ]
        data['divicion_data'] = {'nombre': direccion.nombre, 'estado': 'Activo' if direccion.esta_activa else 'Inactivo'}
        data['dep_inc'] = departamento_incidencias
        data['max_total'] = max_total

    elif group_name == "Departamento":
        departamento = Departamento.objects.get(encargado=request.user.id)
        #incidencias
        incidencias_departamento = Incidencia.objects.filter(encuesta__tipo_incidencia__departamento__id=departamento.id)
        cuadrillas_departamento = Cuadrilla.objects.filter(departamento__id=departamento.id)
        historial_inc = incidencias_departamento.order_by("-updated_at").values('encuesta__titulo', 'prioridad', 'estado', 'updated_at')[:5]
        n_inc = incidencias_departamento.count()
        n_inc_abierta = incidencias_departamento.filter(estado="abierta").count()
        n_inc_derivadas = incidencias_departamento.filter(estado="derivada").count()
        n_inc_proceso = incidencias_departamento.filter(estado="proceso").count()
        n_inc_finalizada = incidencias_departamento.filter(estado="finalizada").count()
        n_inc_cerrada = incidencias_departamento.filter(estado="cerrada").count()
        n_inc_rechazada = incidencias_departamento.filter(estado="rechazada").count()
        n_cuadrillas = cuadrillas_departamento.count()
        cuadrillas_data = cuadrillas_departamento.values('nombre', 'encargado__username', 'esta_activa')

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
        data['divicion_data'] = {'nombre': departamento.nombre, 'estado': 'Activo' if departamento.esta_activo else 'Inactivo'}
        data['historial_inc'] = list(historial_inc)
        data["cuadrillas_data"] = list(cuadrillas_data)

    elif group_name == "Cuadrilla":
        cuadrilla = Cuadrilla.objects.get(encargado__id=request.user.id)
        #incidencias
        incidencias_cuadrilla = Incidencia.objects.filter(cuadrilla__id=request.user.id)
        n_inc = incidencias_cuadrilla.count()
        n_inc_abierta = incidencias_cuadrilla.filter(estado="abierta").count()
        n_inc_derivadas = incidencias_cuadrilla.filter(estado="derivada").count()
        n_inc_proceso = incidencias_cuadrilla.filter(estado="proceso").count()
        n_inc_finalizada = incidencias_cuadrilla.filter(estado="finalizada").count()
        n_inc_cerrada = incidencias_cuadrilla.filter(estado="cerrada").count()
        n_inc_rechazada = incidencias_cuadrilla.filter(estado="rechazada").count()

        hoy = localtime()
        n_inc_resueltas_mes = incidencias_cuadrilla.filter(updated_at__year=hoy.year, updated_at__month=hoy.month, estado='cerrada').count()
        n_inc_asignadas_mes = incidencias_cuadrilla.filter(created_at__year=hoy.year, created_at__month=hoy.month).count()

        data["datos"] = [
            ("Total de incidencias", n_inc, "󱉫"),
            ("Incidencias derivadas", n_inc_derivadas, "󰏡"),
            ("Incidencias en proceso", n_inc_proceso, ""),
            ("Incidencias finalizadas", n_inc_finalizada, ""),
            ("Incidencias cerradas", n_inc_cerrada, "󰅚"),
        ]
        data['divicion_data'] = {'nombre': cuadrilla.departamento.nombre, 'estado': 'Activo' if cuadrilla.esta_activa else 'Inactivo'}
        data["n_inc_resueltas_mes"] = n_inc_resueltas_mes
        data["fecha"] = hoy
        data["porcentaje_completado"] = round(n_inc_resueltas_mes * 100 / n_inc_asignadas_mes) if n_inc_asignadas_mes !=0 else 0

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

        hoy = localtime()
        n_inc_resueltas_mes = incidencias_territorial.filter(updated_at__year=hoy.year, updated_at__month=hoy.month, estado='cerrada').count()
        n_inc_creadas_mes = incidencias_territorial.filter(created_at__year=hoy.year, created_at__month=hoy.month).count()

        data["datos"] = [
            ("Total de incidencias", n_inc, "󱉫"),
            ("Incidencias abiertas", n_inc_abierta, ""),
            ("Incidencias derivadas", n_inc_derivadas, "󰏡"),
            ("Incidencias en proceso", n_inc_proceso, ""),
            ("Incidencias finalizadas", n_inc_finalizada, ""),
            ("Incidencias cerradas", n_inc_cerrada, "󰅚"),
            ("Incidencias rechazadas", n_inc_rechazada, "")
        ]
        if profile.direccion:
            data["divicion_data"] = {'nombre': profile.direccion.nombre}
        data["n_inc_resueltas_mes"] = n_inc_resueltas_mes
        data["n_inc_creadas_mes"] = n_inc_creadas_mes
        data["fecha"] = hoy
        data["promedio_diario"] = round(n_inc_resueltas_mes / hoy.day,2)

    template_name = 'core/dashboard.html'
    return render(request, template_name, data)

def territorial_crear_incidencia(request):
    return redirect('crear_incidencia')
