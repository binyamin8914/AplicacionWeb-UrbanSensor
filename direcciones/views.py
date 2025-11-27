# direcciones/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.db import IntegrityError

from registration.models import Profile
from .models import Direccion




@login_required
def direccion_listar(request):
    profile = Profile.objects.get(user=request.user)
    if profile.group.name != "SECPLA":
        messages.info(request, "No tienes permisos.")
        return redirect("logout")

    filtro_estado = request.GET.get("estado")
    direcciones = Direccion.objects.all()
    if filtro_estado == "Activo":
        direcciones = direcciones.filter(esta_activa=True)
    elif filtro_estado == "Inactivo":
        direcciones = direcciones.filter(esta_activa=False)

    direcciones = direcciones.order_by("nombre")

    context = {
        "titulo": "Gestión de Direcciones",
        "direcciones": direcciones,
        "current_filtro_estado": filtro_estado,
        "group_name": profile.group.name,
    }
    return render(request, "direcciones/direccion_listar.html", context)


@login_required
def direccion_actualizar(request, direccion_id=None):
    """
    Crear/Editar Dirección.
    - Si viene direccion_id => editar
    - Si no => crear
    """
    profile = Profile.objects.get(user=request.user)
    if profile.group.name != "SECPLA":
        messages.info(request, "No tienes permisos.")
        return redirect("logout")

    if direccion_id is not None:
        direccion = get_object_or_404(Direccion, pk=direccion_id)
        titulo_pagina = "Editar Dirección"
    else:
        direccion = None
        titulo_pagina = "Crear Nueva Dirección"

    if request.method == "POST":
        nombre = request.POST.get("nombre")
        encargado_id = request.POST.get("encargado")

        if not nombre or not encargado_id:
            messages.error(request, "Nombre y Encargado son obligatorios.")
        else:
            encargado = get_object_or_404(User, pk=encargado_id)
            try:
                if direccion:
                    direccion.nombre = nombre
                    direccion.encargado = encargado
                    direccion.save()
                    messages.success(request, "¡Dirección actualizada con éxito!")
                else:
                    Direccion.objects.create(
                        nombre=nombre,
                        encargado=encargado,
                        esta_activa=True,
                    )
                    messages.success(request, "¡Dirección creada con éxito!")

                return redirect("direccion_listar")

            except IntegrityError:
                messages.error(
                    request,
                    f"Error: El usuario '{encargado.username}' ya es encargado de otra dirección. "
                    "Por favor, seleccione un usuario diferente."
                )

    
    try:
        grupo_direccion = Group.objects.get(name="Direccion")
        encargados = User.objects.filter(groups=grupo_direccion)
    except Group.DoesNotExist:
        encargados = User.objects.filter(is_superuser=True)

    context = {
        "titulo_pagina": titulo_pagina,
        "direccion": direccion,
        "encargados": encargados,
        "group_name": profile.group.name,
    }
    return render(request, "direcciones/direccion_actualizar.html", context)


@login_required
def direccion_ver(request, direccion_id):
    profile = Profile.objects.get(user=request.user)
    if profile.group.name != "SECPLA":
        messages.info(request, "No tienes permisos.")
        return redirect("logout")

    direccion = get_object_or_404(Direccion, pk=direccion_id)
    return render(
        request,
        "direcciones/direccion_ver.html",
        {"direccion": direccion, "group_name": profile.group.name},
    )


@login_required
def direccion_bloquear(request, direccion_id):
    profile = Profile.objects.get(user=request.user)
    if profile.group.name != "SECPLA":
        messages.info(request, "No tienes permisos.")
        return redirect("logout")

    direccion = get_object_or_404(Direccion, pk=direccion_id)
    direccion.esta_activa = not direccion.esta_activa
    direccion.save()
    estado = "activada" if direccion.esta_activa else "bloqueada"
    messages.success(request, f"Dirección {estado} correctamente.")
    return redirect("direccion_listar")
