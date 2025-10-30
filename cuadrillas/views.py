from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from registration.models import Profile
from .models import Departamento, Cuadrilla

# --- CRUD Cuadrilla ---

@login_required
def cuadrilla_listar(request):
    profile = Profile.objects.get(user=request.user)
    if profile.group.name != "SECPLA":
        messages.add_message(request, messages.INFO, "No tienes permisos.")
        return redirect("logout")
    cuadrillas = Cuadrilla.objects.all()
    return render(request, "cuadrillas/cuadrilla_listar.html", {"cuadrillas": cuadrillas, "group_name": profile.group.name})

@login_required
def cuadrilla_actualizar(request, cuadrilla_id=None):
    profile = Profile.objects.get(user=request.user)
    if profile.group.name != "SECPLA":
        messages.add_message(request, messages.INFO, "No tienes permisos.")
        return redirect("logout")

    if cuadrilla_id:
        cuadrilla = Cuadrilla.objects.filter(pk=cuadrilla_id).first()
        if not cuadrilla:
            messages.add_message(request, messages.INFO, "Cuadrilla no encontrada.")
            return redirect("cuadrilla_listar")
    else:
        cuadrilla = None

    if request.method == "POST":
        nombre = request.POST.get("nombre")
        encargado_id = request.POST.get("encargado")
        departamento_id = request.POST.get("departamento")
        encargado = User.objects.get(pk=encargado_id)
        departamento = Departamento.objects.get(pk=departamento_id)
        if cuadrilla:  # Edición
            cuadrilla.nombre = nombre
            cuadrilla.encargado = encargado
            cuadrilla.departamento = departamento
            cuadrilla.save()
            messages.add_message(request, messages.INFO, "Cuadrilla actualizada correctamente.")
        else:  # Creación
            Cuadrilla.objects.create(
                nombre=nombre, encargado=encargado, departamento=departamento
            )
            messages.add_message(request, messages.INFO, "Cuadrilla creada correctamente.")
        return redirect("cuadrilla_listar")

    encargados = User.objects.filter(profile__group__name="Cuadrilla")
    departamentos = Departamento.objects.filter(esta_activo=True)
    return render(request, "cuadrillas/cuadrilla_actualizar.html", {
        "cuadrilla": cuadrilla,
        "encargados": encargados,
        "departamentos": departamentos, 
        "group_name": profile.group.name
    })

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