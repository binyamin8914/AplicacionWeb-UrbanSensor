from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.contrib import messages
from registration.models import Profile

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
    usuarios_db = User.objects.all().order_by('username')
    datos = {
        'titulo': "Gestión de Usuarios",
        'url': {'name': 'usuario_actualizar', 'label': 'Nuevo Usuario'},
        'titulos': ['Usuario', 'Nombre', 'Apellido', 'Correo', 'Teléfono', 'Perfil', 'Estado'],
        'back': 'dashboard',
        'filas': [{
                "id": usuario.id,
                'acciones': [{'url': 'usuario_ver', 'name': 'Ver', 'ic': ''},
                    {'url': 'usuario_actualizar','name': 'Editar','ic': ''},
                    {'url': 'usuario_bloquear', 'name': 'Bloquear' if usuario.is_active else 'Activar', 'ic': '' if usuario.is_active else ''}
                ],
                "columnas": [usuario.username, usuario.first_name, usuario.last_name,
                    usuario.email, usuario.profile.telefono, usuario.profile.group.name,
                    'Activo' if usuario.is_active else 'Bloqueado',   
                ],
                'clases': ['', '', '', '', '', '', 'Activo' if usuario.is_active else 'Inactivo']
            }
            for usuario in usuarios_db
        ],
        'tieneAcciones': True,
        "group_name": profile.group.name
    }
    return render(request, "administracion/usuarios_listar.html", datos)

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
            return redirect("usuarios_listar")
    else:
        user = None
        user_profile = None

    if request.method == "POST":
        username = request.POST.get("username")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        group_name = request.POST.get("group")
        telefono = request.POST.get("telefono")

        if user:  # Edición
            user.first_name = first_name
            user.last_name = last_name
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
                return redirect("usuario_actualizar")
            if User.objects.filter(username=username).exists():
                messages.add_message(request, messages.INFO, "Usuario ya existe.")
                return redirect("usuario_actualizar")
            user = User.objects.create_user(username=username, email=email, first_name=first_name, last_name=last_name)
            user.set_password(password)
            user.is_active = True
            user.save()
            group = Group.objects.get(name=group_name)
            user.groups.add(group)
            Profile.objects.create(user=user, group=group, telefono=telefono)
            messages.add_message(request, messages.INFO, "Usuario creado correctamente.")
        return redirect("usuarios_listar")

    grupos = Group.objects.all()
    return render(request, "administracion/usuarios_actualizar.html", {
        "usuario": user,
        "user_profile": user_profile,
        "grupos": grupos,
        "group_name": profile.group.name
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
        return redirect("usuarios_listar")
    user.is_active = not user.is_active
    user.save()
    estado = "activado" if user.is_active else "bloqueado"
    messages.add_message(request, messages.INFO, f"Usuario {estado} correctamente.")
    return redirect("usuarios_listar")

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
        return redirect("usuarios_listar")
    return render(request, "administracion/usuarios_ver.html", {"usuario": user, "user_profile": user_profile, "group_name": profile.group.name})
