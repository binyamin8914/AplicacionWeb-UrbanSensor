from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User, Group # <-- ¡Añadido Group!
from registration.models import Profile
from departamentos.models import Departamento # <-- ¡Cambiado!
from .models import Cuadrilla

# --- ¡¡IMPORTANTE: Importa el manejador de errores!! ---
from django.db import IntegrityError 

# --- CRUD Cuadrilla ---

@login_required
def cuadrilla_listar(request):
    profile = Profile.objects.get(user=request.user)
    if profile.group.name != "SECPLA":
        messages.add_message(request, messages.INFO, "No tienes permisos.")
        return redirect("logout")

    # --- Lógica de Filtro AÑADIDA ---
    filtro_estado = request.GET.get('estado')
    filtro_depto = request.GET.get('departamento')

    cuadrillas = Cuadrilla.objects.select_related('departamento').all()

    if filtro_estado == 'Activo':
        cuadrillas = cuadrillas.filter(esta_activa=True)
    elif filtro_estado == 'Inactivo':
        cuadrillas = cuadrillas.filter(esta_activa=False)
        
    if filtro_depto:
        cuadrillas = cuadrillas.filter(departamento__id=filtro_depto)

    cuadrillas = cuadrillas.order_by('nombre')
    
    # Contexto para la plantilla Bootstrap
    context = {
        'titulo': 'Gestión de Cuadrillas',
        'cuadrillas': cuadrillas, # Pasamos la queryset
        'departamentos_filtro': Departamento.objects.filter(esta_activo=True), # Para el dropdown
        'current_filtro_estado': filtro_estado,
        'current_filtro_depto': filtro_depto,
        "group_name": profile.group.name,
    }
    return render(request, "cuadrillas/cuadrilla_listar.html", context)


@login_required
def cuadrilla_actualizar(request, cuadrilla_id=None):
    profile = Profile.objects.get(user=request.user)
    if profile.group.name != "SECPLA":
        messages.add_message(request, messages.INFO, "No tienes permisos.")
        return redirect("logout")

    if cuadrilla_id:
        cuadrilla = get_object_or_404(Cuadrilla, pk=cuadrilla_id) # Usamos get_object_or_404
        titulo_pagina = "Editar Cuadrilla"
    else:
        cuadrilla = None
        titulo_pagina = "Crear Nueva Cuadrilla"

    if request.method == "POST":
        nombre = request.POST.get("nombre")
        encargado_id = request.POST.get("encargado")
        departamento_id = request.POST.get("departamento")

        if not all([nombre, encargado_id, departamento_id]):
            messages.error(request, "Nombre, Encargado y Departamento son obligatorios.")
        else:
            encargado = get_object_or_404(User, pk=encargado_id)
            departamento = get_object_or_404(Departamento, pk=departamento_id)
            
            # --- ¡¡AQUÍ ESTÁ EL BLOQUE TRY/EXCEPT!! ---
            try:
                if cuadrilla:  # Edición
                    cuadrilla.nombre = nombre
                    cuadrilla.encargado = encargado
                    cuadrilla.departamento = departamento
                    cuadrilla.save()
                    messages.success(request, "Cuadrilla actualizada correctamente.")
                else:  # Creación
                    Cuadrilla.objects.create(
                        nombre=nombre, 
                        encargado=encargado, 
                        departamento=departamento,
                        esta_activa=True
                    )
                    messages.success(request, "Cuadrilla creada correctamente.")
                
                return redirect("cuadrilla_listar") # Redirige solo si todo va bien

            except IntegrityError:
                # ¡Atrapamos el error de llave duplicada!
                messages.error(request, f"Error: El usuario '{encargado.username}' ya es encargado de otra cuadrilla. Por favor, seleccione un usuario diferente.")
                # No redirigimos

    # --- Lógica GET (o si el POST falló) ---
    try:
        grupo_cuadrilla = Group.objects.get(name="Cuadrilla")
        encargados = User.objects.filter(groups=grupo_cuadrilla)
    except Group.DoesNotExist:
        encargados = User.objects.all() # Plan B
    
    departamentos = Departamento.objects.filter(esta_activo=True) # Para el desplegable

    context = {
        "titulo_pagina": titulo_pagina,
        "cuadrilla": cuadrilla,
        "encargados": encargados,
        "departamentos": departamentos,
        "group_name": profile.group.name
    }
    return render(request, "cuadrillas/cuadrilla_actualizar.html", context)


@login_required
def cuadrilla_ver(request, cuadrilla_id):
    profile = Profile.objects.get(user=request.user)
    if profile.group.name != "SECPLA":
        messages.add_message(request, messages.INFO, "No tienes permisos.")
        return redirect("logout")
    cuadrilla = get_object_or_404(Cuadrilla, pk=cuadrilla_id)
    return render(request, "cuadrillas/cuadrilla_ver.html", {"cuadrilla": cuadrilla, "group_name": profile.group.name})

@login_required
def cuadrilla_bloquear(request, cuadrilla_id):
    profile = Profile.objects.get(user=request.user)
    if profile.group.name != "SECPLA":
        messages.add_message(request, messages.INFO, "No tienes permisos.")
        return redirect("logout")
    cuadrilla = get_object_or_404(Cuadrilla, pk=cuadrilla_id)
    cuadrilla.esta_activa = not cuadrilla.esta_activa
    cuadrilla.save()
    estado = "activada" if cuadrilla.esta_activa else "bloqueada"
    messages.success(request, f"Cuadrilla {estado} correctamente.")
    return redirect("cuadrilla_listar")