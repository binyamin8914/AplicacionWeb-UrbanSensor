from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.contrib import messages
from registration.models import Profile
from .models import Direccion, Departamento, Cuadrilla

# --- CRUD Usuarios ---

@login_required
def usuarios_listar(request):
    try:
        profile = Profile.objects.get(user=request.user)
    except:
        messages.add_message(request, messages.INFO, "Error obteniendo perfil.")
        return redirect("logout")
    if profile.group.name != "SECPLA":
        messages.add_message(request, messages.INFO, "No tienes permisos.")
        return redirect("logout")
    usuarios = User.objects.all().order_by('username')
    return render(request, "administracion/usuarios_listar.html", {"usuarios": usuarios})

@login_required
def usuario_actualizar(request, user_id=None):
    try:
        profile = Profile.objects.get(user=request.user)
    except:
        messages.add_message(request, messages.INFO, "Error obteniendo perfil.")
        return redirect("logout")
    if profile.group.name != "SECPLA":
        messages.add_message(request, messages.INFO, "No tienes permisos.")
        return redirect("logout")

    if user_id:
        try:
            user = User.objects.get(pk=user_id)
            user_profile = Profile.objects.get(user=user)
        except:
            messages.add_message(request, messages.INFO, "Usuario no encontrado.")
            return redirect("administracion:usuarios_listar")
    else:
        user = None
        user_profile = None

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        group_name = request.POST.get("group")
        telefono = request.POST.get("telefono")

        if user:  # Edición
            user.email = email
            if password:
                user.set_password(password)
            group = Group.objects.get(name=group_name)
            user.groups.clear()
            user.groups.add(group)
            user.save()
            user_profile.group = group
            user_profile.telefono = telefono
            user_profile.save()
            messages.add_message(request, messages.INFO, "Usuario actualizado correctamente.")
        else:  # Creación
            if not (username and email and password and group_name):
                messages.add_message(request, messages.INFO, "Faltan datos obligatorios.")
                return redirect("administracion]:usuario_actualizar")
            if User.objects.filter(username=username).exists():
                messages.add_message(request, messages.INFO, "Usuario ya existe.")
                return redirect("administracion:usuario_actualizar")
            user = User.objects.create_user(username=username, email=email)
            user.set_password(password)
            user.is_active = True
            user.save()
            group = Group.objects.get(name=group_name)
            user.groups.add(group)
            Profile.objects.create(user=user, group=group, telefono=telefono)
            messages.add_message(request, messages.INFO, "Usuario creado correctamente.")
        return redirect("administracion:usuarios_listar")

    grupos = Group.objects.all()
    return render(request, "administracion/usuario_actualizar.html", {
        "usuario": user,
        "user_profile": user_profile,
        "grupos": grupos
    })

@login_required
def usuario_bloquear(request, user_id):
    try:
        profile = Profile.objects.get(user=request.user)
    except:
        messages.add_message(request, messages.INFO, "Error obteniendo perfil.")
        return redirect("logout")
    if profile.group.name != "SECPLA":
        messages.add_message(request, messages.INFO, "No tienes permisos.")
        return redirect("logout")
    try:
        user = User.objects.get(pk=user_id)
    except:
        messages.add_message(request, messages.INFO, "Usuario no encontrado.")
        return redirect("administracion:usuarios_listar")
    user.is_active = not user.is_active
    user.save()
    estado = "activado" if user.is_active else "bloqueado"
    messages.add_message(request, messages.INFO, f"Usuario {estado} correctamente.")
    return redirect("administracion:usuarios_listar")

@login_required
def usuario_ver(request, user_id):
    try:
        profile = Profile.objects.get(user=request.user)
    except:
        messages.add_message(request, messages.INFO, "Error obteniendo perfil.")
        return redirect("logout")
    if profile.group.name != "SECPLA":
        messages.add_message(request, messages.INFO, "No tienes permisos.")
        return redirect("logout")
    try:
        user = User.objects.get(pk=user_id)
        user_profile = Profile.objects.get(user=user)
    except:
        messages.add_message(request, messages.INFO, "Usuario no encontrado.")
        return redirect("administracion:usuarios_listar")
    return render(request, "administracion/usuarios_ver.html", {"usuario": user, "user_profile": user_profile})

# --- CRUD Direccion ---

@login_required
def direccion_listar(request):
    profile = Profile.objects.get(user=request.user)
    if profile.group.name != "SECPLA":
        messages.add_message(request, messages.INFO, "No tienes permisos.")
        return redirect("logout")
    direcciones = Direccion.objects.all()
    return render(request, "administracion/direccion_listar.html", {"direcciones": direcciones})

@login_required
def direccion_actualizar(request, direccion_id=None):
    profile = Profile.objects.get(user=request.user)
    if profile.group.name != "SECPLA":
        messages.add_message(request, messages.INFO, "No tienes permisos.")
        return redirect("logout")

    if direccion_id:
        direccion = Direccion.objects.filter(pk=direccion_id).first()
        if not direccion:
            messages.add_message(request, messages.INFO, "Dirección no encontrada.")
            return redirect("administracion:direccion_listar")
    else:
        direccion = None

    if request.method == "POST":
        nombre = request.POST.get("nombre")
        encargado_id = request.POST.get("encargado")
        correo_encargado = request.POST.get("correo_encargado")
        encargado = User.objects.get(pk=encargado_id)
        if direccion:  # Edición
            direccion.nombre = nombre
            direccion.encargado = encargado
            direccion.correo_encargado = correo_encargado
            direccion.save()
            messages.add_message(request, messages.INFO, "Dirección actualizada correctamente.")
        else:  # Creación
            Direccion.objects.create(
                nombre=nombre, encargado=encargado, correo_encargado=correo_encargado
            )
            messages.add_message(request, messages.INFO, "Dirección creada correctamente.")
        return redirect("administracion:direccion_listar")

    encargados = User.objects.all()
    return render(request, "administracion/direccion_actualizar.html", {
        "direccion": direccion,
        "encargados": encargados
    })

@login_required
def direccion_ver(request, direccion_id):
    profile = Profile.objects.get(user=request.user)
    if profile.group.name != "SECPLA":
        messages.add_message(request, messages.INFO, "No tienes permisos.")
        return redirect("logout")
    direccion = get_object_or_404(Direccion, pk=direccion_id)
    return render(request, "administracion/direccion_ver.html", {"direccion": direccion})

@login_required
def direccion_bloquear(request, direccion_id):
    profile = Profile.objects.get(user=request.user)
    if profile.group.name != "SECPLA":
        messages.add_message(request, messages.INFO, "No tienes permisos.")
        return redirect("logout")
    direccion = get_object_or_404(Direccion, pk=direccion_id)
    direccion.esta_activa = not direccion.esta_activa
    direccion.save()
    estado = "activada" if direccion.esta_activa else "bloqueada"
    messages.success(request, f"Dirección {estado} correctamente.")
    return redirect("administracion:direccion_listar")

# --- CRUD Departamento ---

@login_required
def departamento_listar(request):
    profile = Profile.objects.get(user=request.user)
    if profile.group.name != "SECPLA":
        messages.add_message(request, messages.INFO, "No tienes permisos.")
        return redirect("logout")
    departamentos = Departamento.objects.all()
    return render(request, "administracion/departamento_listar.html", {"departamentos": departamentos})

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
            return redirect("administracion:departamento_listar")
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
        return redirect("administracion:departamento_listar")

    encargados = User.objects.all()
    direcciones = Direccion.objects.filter(esta_activa=True)
    return render(request, "administracion/departamento_actualizar.html", {
        "departamento": departamento,
        "encargados": encargados,
        "direcciones": direcciones
    })

@login_required
def departamento_ver(request, departamento_id):
    profile = Profile.objects.get(user=request.user)
    if profile.group.name != "SECPLA":
        messages.add_message(request, messages.INFO, "No tienes permisos.")
        return redirect("logout")
    departamento = get_object_or_404(Departamento, pk=departamento_id)
    return render(request, "administracion/departamento_ver.html", {"departamento": departamento})

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
    return redirect("administracion:departamento_listar")

# --- CRUD Cuadrilla ---

@login_required
def cuadrilla_listar(request):
    profile = Profile.objects.get(user=request.user)
    if profile.group.name != "SECPLA":
        messages.add_message(request, messages.INFO, "No tienes permisos.")
        return redirect("logout")
    cuadrillas = Cuadrilla.objects.all()
    return render(request, "administracion/cuadrilla_listar.html", {"cuadrillas": cuadrillas})

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
            return redirect("administracion:cuadrilla_listar")
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
        return redirect("administracion:cuadrilla_listar")

    encargados = User.objects.all()
    departamentos = Departamento.objects.filter(esta_activo=True)
    return render(request, "administracion/cuadrilla_actualizar.html", {
        "cuadrilla": cuadrilla,
        "encargados": encargados,
        "departamentos": departamentos
    })

@login_required
def cuadrilla_ver(request, cuadrilla_id):
    profile = Profile.objects.get(user=request.user)
    if profile.group.name != "SECPLA":
        messages.add_message(request, messages.INFO, "No tienes permisos.")
        return redirect("logout")
    cuadrilla = get_object_or_404(Cuadrilla, pk=cuadrilla_id)
    return render(request, "administracion/cuadrilla_ver.html", {"cuadrilla": cuadrilla})

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
    return redirect("administracion:cuadrilla_listar")