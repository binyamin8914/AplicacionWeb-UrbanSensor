from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User, Group # <-- ¡Añadido Group!
from registration.models import Profile
from .models import Departamento
from direcciones.models import Direccion # <-- ¡Cambiado!
from incidencias.models import Incidencia
from cuadrillas.models import Cuadrilla
from django.db.models import Count
from django.db import IntegrityError # --- Importa el manejador de errores!! ---

# --- CRUD Departamento ---

@login_required
def departamento_listar(request):
    profile = Profile.objects.get(user=request.user)
    if profile.group.name not in ["SECPLA", "Direccion"]:
        messages.add_message(request, messages.INFO, "No tienes permisos.")
        return redirect("logout")

    # --- Lógica de Filtro AÑADIDA ---
    filtro_estado = request.GET.get('estado')
    filtro_direccion = request.GET.get('direccion')
    
    departamentos = Departamento.objects.select_related('direccion').all()
    if profile.group.name == "Direccion":
        direccion = Direccion.objects.get(encargado__id=profile.id)
        departamentos = departamentos.filter(direccion__id=direccion.id)

    if filtro_estado == 'Activo':
        departamentos = departamentos.filter(esta_activo=True)
    elif filtro_estado == 'Inactivo':
        departamentos = departamentos.filter(esta_activo=False)
        
    if filtro_direccion:
        # Filtramos por el ID de la dirección
        departamentos = departamentos.filter(direccion__id=filtro_direccion) 

    departamentos = departamentos.order_by('nombre')
    
    # Contexto para la plantilla Bootstrap
    context = {
        'titulo': 'Gestión de Departamentos',
        'departamentos': departamentos, # Pasamos la queryset directamente
        'direcciones_filtro': Direccion.objects.filter(esta_activa=True), # Para el dropdown
        'current_filtro_estado': filtro_estado,
        'current_filtro_direccion': filtro_direccion,
        "group_name": profile.group.name,
    }
    return render(request, "departamentos/departamento_listar.html", context)


@login_required
def departamento_actualizar(request, departamento_id=None):
    profile = Profile.objects.get(user=request.user)
    if profile.group.name not in ["SECPLA", "Direccion"]:
        messages.add_message(request, messages.INFO, "No tienes permisos.")
        return redirect("logout")

    if departamento_id:
        departamento = get_object_or_404(Departamento, pk=departamento_id) # Usamos get_object_or_404
        titulo_pagina = "Editar Departamento"
    else:
        departamento = None
        titulo_pagina = "Crear Nuevo Departamento"

    if request.method == "POST":
        nombre = request.POST.get("nombre")
        encargado_id = request.POST.get("encargado")
        # correo_encargado = request.POST.get("correo_encargado")
        direccion_id = request.POST.get("direccion")

        if not all([nombre, encargado_id, direccion_id]):
            messages.error(request, "Nombre, Encargado y Dirección son obligatorios.")
        else:
            encargado = get_object_or_404(User, pk=encargado_id)
            direccion = get_object_or_404(Direccion, pk=direccion_id)
            
            # --- ¡¡AQUÍ ESTÁ EL BLOQUE TRY/EXCEPT!! ---
            try:
                if departamento:  # Edición
                    departamento.nombre = nombre
                    departamento.encargado = encargado
                    # departamento.correo_encargado = correo_encargado
                    departamento.direccion = direccion
                    departamento.save()
                    messages.success(request, "Departamento actualizado correctamente.")
                else:  # Creación
                    Departamento.objects.create(
                        nombre=nombre, 
                        encargado=encargado, 
                        # correo_encargado=correo_encargado,
                        direccion=direccion,
                        esta_activo=True
                    )
                    messages.success(request, "Departamento creado correctamente.")
                
                return redirect("departamento_listar") # Redirige solo si todo va bien

            except IntegrityError:
                # ¡Atrapamos el error de llave duplicada!
                messages.error(request, f"Error: El usuario '{encargado.username}' ya es encargado de otro departamento. Por favor, seleccione un usuario diferente.")
                # No redirigimos, para que el usuario vea el error

    # --- Lógica GET (o si el POST falló) ---
    try:
        grupo_depto = Group.objects.get(name="Departamento")
        encargados = User.objects.filter(groups=grupo_depto)
    except Group.DoesNotExist:
        encargados = User.objects.filter(is_superuser=True) # Plan B
    
    direcciones = Direccion.objects.filter(esta_activa=True) # Para el desplegable

    context = {
        "titulo_pagina": titulo_pagina,
        "departamento": departamento,
        "encargados": encargados,
        "direcciones": direcciones,
        "group_name": profile.group.name
    }
    return render(request, "departamentos/departamento_actualizar.html", context)


@login_required
def departamento_ver(request, departamento_id):
    profile = Profile.objects.get(user=request.user)
    if profile.group.name not in ["SECPLA", "Direccion"]:
        messages.add_message(request, messages.INFO, "No tienes permisos.")
        return redirect("logout")

    departamento = get_object_or_404(Departamento, pk=departamento_id)
    return render(request, "departamentos/departamento_ver.html", {
        "departamento": departamento,
        "group_name": profile.group.name
    })


@login_required
def departamento_bloquear(request, departamento_id):
    profile = Profile.objects.get(user=request.user)
    if profile.group.name not in ["SECPLA", "Direccion"]:
        messages.add_message(request, messages.INFO, "No tienes permisos.")
        return redirect("logout")

    departamento = get_object_or_404(Departamento, pk=departamento_id)
    departamento.esta_activo = not departamento.esta_activo
    departamento.save()
    estado = "activado" if departamento.esta_activo else "bloqueado"
    messages.success(request, f"Departamento {estado} correctamente.")
    return redirect("departamento_listar")


@login_required
def departamento_dashboard(request):

    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        messages.error(request, "Error obteniendo perfil.")
        return redirect("logout")
    departamento = Departamento.objects.filter(encargado=request.user).first()
    if not departamento:
        messages.info(request, "No eres encargado de ningún departamento.")
        return redirect("logout")
    incidencias = Incidencia.objects.filter(encuesta__departamento=departamento)
    estados_count = incidencias.values('estado').annotate(total=Count('id'))
    counts = {item['estado']: item['total'] for item in estados_count}
    context = {
        "departamento": departamento,
        "counts": counts,
        "group_name": profile.group.name
    }
    return render(request, "departamentos/dashboard_departamento.html", context)

@login_required
def incidencias_por_estado(request, estado=None):
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        messages.error(request, "Error obteniendo perfil.")
        return redirect("logout")
    departamento = Departamento.objects.filter(encargado=request.user).first()
    if not departamento:
        messages.info(request, "No eres encargado de ningún departamento.")
        return redirect("logout")
    if estado:
        incidencias = Incidencia.objects.filter(encuesta__departamento=departamento, estado=estado).order_by('-created_at')
    else:
        incidencias = Incidencia.objects.filter(encuesta__departamento=departamento).order_by('-created_at')
    context = {
        "departamento": departamento,
        "incidencias": incidencias,
        "estado": estado,
        "group_name": profile.group.name
    }
    return render(request, "incidencias/gestion_incidencias.html", context)

@login_required
def incidencia_ver_y_derivar(request, incidencia_id):
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        messages.error(request, "Error obteniendo perfil.")
        return redirect("logout")
    departamento = Departamento.objects.filter(encargado=request.user).first()
    if not departamento:
        messages.info(request, "No eres encargado de ningún departamento.")
        return redirect("logout")
    incidencia = get_object_or_404(Incidencia, pk=incidencia_id, encuesta__departamento=departamento)
    cuadrillas = Cuadrilla.objects.filter(departamento=departamento, esta_activa=True)
    if request.method == "POST":
        cuadrilla_id = request.POST.get("cuadrilla")
        if not cuadrilla_id:
            messages.info(request, "Selecciona una cuadrilla.")
            return redirect("incidencia_ver_y_derivar", incidencia_id=incidencia.id)
        try:
            cuadrilla = Cuadrilla.objects.get(pk=cuadrilla_id)
        except Cuadrilla.DoesNotExist:
            messages.error(request, "Cuadrilla no encontrada.")
            return redirect("incidencia_ver_y_derivar", incidencia_id=incidencia.id)
        if cuadrilla.departamento_id != departamento.id:
            messages.error(request, "La cuadrilla seleccionada no pertenece a tu departamento.")
            return redirect("incidencia_ver_y_derivar", incidencia_id=incidencia.id)
        incidencia.cuadrilla = cuadrilla
        incidencia.estado = 'derivada'
        incidencia.save()
        messages.success(request, "Incidencia derivada a cuadrilla correctamente.")
        return redirect("incidencias_por_estado", estado="derivada")
    context = {
        "incidencia": incidencia,
        "cuadrillas": cuadrillas,
        "group_name": profile.group.name
    }
    return render(request, "incidencias/detalle_incidencia.html", context)
