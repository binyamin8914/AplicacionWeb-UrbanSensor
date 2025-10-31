from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from registration.models import Profile
from .models import Departamento, Direccion

# --- CRUD Departamento ---

@login_required
def departamento_listar(request):
    profile = Profile.objects.get(user=request.user)
    if profile.group.name not in ["SECPLA", "Direccion"]:
        messages.add_message(request, messages.INFO, "No tienes permisos.")
        return redirect("logout")
    if profile.group.name == "Direccion":
        # Solo puede ver los departamentos que esten asignados a su direccion
        direccion = Direccion.objects.get(encargado_id=profile.id)
        departamentos = Departamento.objects.filter(direccion_id=direccion.id)
    else:
        departamentos = Departamento.objects.all()
    return render(request, "departamentos/departamento_listar.html", {"departamentos": departamentos, "group_name": profile.group.name})

@login_required
def departamento_actualizar(request, departamento_id=None):
    profile = Profile.objects.get(user=request.user)
    if profile.group.name != "SECPLA":
        messages.add_message(request, messages.INFO, "No tienes permisos.")
        return redirect("logout")

    if departamento_id:
        departamento = Departamento.objects.filter(pk=departamento_id).first()
        if not departamento:
            messages.add_message(request, messages.INFO, "Departamento no encontrado.")
            return redirect("departamento_listar")
    else:
        departamento = None

    if request.method == "POST":
        nombre = request.POST.get("nombre")
        encargado_id = request.POST.get("encargado")
        correo_encargado = request.POST.get("correo_encargado")
        direccion_id = request.POST.get("direccion")
        encargado = User.objects.get(pk=encargado_id)
        direccion = Direccion.objects.get(pk=direccion_id)
        if departamento:  # Edición
            departamento.nombre = nombre
            departamento.encargado = encargado
            departamento.correo_encargado = correo_encargado
            departamento.direccion = direccion
            departamento.save()
            messages.add_message(request, messages.INFO, "Departamento actualizado correctamente.")
        else:  # Creación
            Departamento.objects.create(
                nombre=nombre, encargado=encargado, correo_encargado=correo_encargado, direccion=direccion
            )
            messages.add_message(request, messages.INFO, "Departamento creado correctamente.")
        return redirect("departamento_listar")

    encargados = User.objects.filter(profile__group__name="Departamento")
    direcciones = Direccion.objects.filter(esta_activa=True)
    return render(request, "departamentos/departamento_actualizar.html", {
        "departamento": departamento,
        "encargados": encargados,
        "direcciones": direcciones,
        "group_name": profile.group.name
    })

@login_required
def departamento_ver(request, departamento_id):
    profile = Profile.objects.get(user=request.user)
    if profile.group.name not in ["SECPLA", "Direccion"]:
        messages.add_message(request, messages.INFO, "No tienes permisos.")
        return redirect("logout")

    departamento = get_object_or_404(Departamento, pk=departamento_id)

    if profile.group.name == "Direccion":
        direccion = Direccion.objects.get(encargado_id=profile.id) # direccion a la que es encargado
        if departamento.direccion.id != direccion.id: # si esta consultando un departamento de otra direccion, no da permiso
            messages.add_message(request, messages.INFO, "No tienes permisos.")
            return redirect("logout")
    
    return render(request, "departamentos/departamento_ver.html", {"departamento": departamento, "group_name": profile.group.name})

@login_required
def departamento_bloquear(request, departamento_id):
    profile = Profile.objects.get(user=request.user)
    if profile.group.name != "SECPLA":
        messages.add_message(request, messages.INFO, "No tienes permisos.")
        return redirect("logout")
    departamento = get_object_or_404(Departamento, pk=departamento_id)
    departamento.esta_activo = not departamento.esta_activo
    departamento.save()
    estado = "activado" if departamento.esta_activo else "bloqueado"
    messages.success(request, f"Departamento {estado} correctamente.")
    return redirect("departamento_listar")
