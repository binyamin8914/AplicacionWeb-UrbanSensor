# apps/administracion/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.contrib import messages
from registration.models import Profile
from direcciones.models import Direccion


# ===================================================================
# --- VISTAS DE USUARIOS (ÚNICO QUE QUEDA EN ESTA APP) ---
# ===================================================================
@login_required
def usuarios_listar(request):
    # Lista de usuarios con filtros por estado y perfil (grupo)
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        messages.add_message(request, messages.INFO, "Error obteniendo perfil.")
        return redirect("logout")

    if profile.group.name != "SECPLA":
        messages.add_message(request, messages.INFO, "No tienes permisos.")
        return redirect("logout")

    filtro_estado = request.GET.get('estado')
    filtro_perfil = request.GET.get('perfil')

    usuarios_db = User.objects.all()

    if filtro_estado == 'Activo':
        usuarios_db = usuarios_db.filter(is_active=True)
    elif filtro_estado == 'Bloqueado':
        usuarios_db = usuarios_db.filter(is_active=False)

    if filtro_perfil:
        usuarios_db = usuarios_db.filter(groups__name=filtro_perfil)

    usuarios_db = usuarios_db.order_by('username')
    grupos_para_filtro = Group.objects.all()

    datos = {
        'titulo': "Gestión de Usuarios",
        'descripcion': "Gestión de todos los usuarios de la plataforma",
        'url': {'name': 'usuario_actualizar', 'label': 'Nuevo Usuario', 'ic': ''},
        'titulos': ['Usuario', 'Nombre', 'Apellido', 'Correo', 'Teléfono', 'Perfil', 'Estado'],
        'back': 'dashboard',
        'filtros': [
            { 'nombre': 'Estado', 'nombre_corto': 'estado', 'opciones': ["Activo", "Bloqueado"]},
            { 'nombre': 'Perfil', 'nombre_corto': 'perfil', 'opciones': [grupo.name for grupo in grupos_para_filtro]}
        ],
        'tieneAcciones': True,
        "group_name": profile.group.name,
        'current_filtro_estado': filtro_estado,
        'current_filtro_perfil': filtro_perfil,
        'filas': []
    }

    for usuario in usuarios_db:
        datos['filas'].append({
            "id": usuario.id,
            'acciones': [
                {'url': 'usuario_ver', 'name': 'Ver', 'ic': ''},
                {'url': 'usuario_actualizar_id', 'name': 'Editar', 'ic': ''},
                {'url': 'usuario_bloquear', 'name': 'Bloquear' if usuario.is_active else 'Activar', 'ic': '' if usuario.is_active else ''}
            ],
            "columnas": [
                usuario.username, usuario.first_name, usuario.last_name,
                usuario.email, getattr(usuario.profile, 'telefono', ''), getattr(usuario.profile.group, 'name', ''),
                'Activo' if usuario.is_active else 'Bloqueado',
            ],
            'clases': ['', '', '', '', '', '', 'Activo' if usuario.is_active else 'Inactivo']
        })

    return render(request, "administracion/usuarios_listar.html", datos)


@login_required
def usuario_actualizar(request, user_id=None):
    # Crear o editar un usuario
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        messages.add_message(request, messages.INFO, "Error obteniendo perfil.")
        return redirect("logout")

    if profile.group.name != "SECPLA":
        messages.add_message(request, messages.INFO, "No tienes permisos.")
        return redirect("logout")

    if user_id:
        try:
            user = User.objects.get(pk=user_id)
            user_profile = Profile.objects.get(user=user)
        except (User.DoesNotExist, Profile.DoesNotExist):
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

        if user:
            # Edición
            user.first_name = first_name or ''
            user.last_name = last_name or ''
            user.email = email or ''
            if password:
                user.set_password(password)
            try:
                group = Group.objects.get(name=group_name)
            except Group.DoesNotExist:
                messages.add_message(request, messages.INFO, "Grupo no válido.")
                return redirect("usuario_actualizar_id", user_id=user.id)

            user.groups.clear()
            user.groups.add(group)
            user.save()

            user_profile.group = group
            user_profile.telefono = telefono or ''
            # ---- NUEVO: asignar dirección solo si es Territorial ----
            if group.name == "Territorial":
                direccion_id = request.POST.get("direccion_id")
                try:
                    direccion = Direccion.objects.get(pk=direccion_id)
                except Direccion.DoesNotExist:
                    messages.add_message(request, messages.INFO, "Debe seleccionar una dirección válida para el territorial.")
                    return redirect("usuario_actualizar_id", user_id=user.id)
                user_profile.direccion = direccion
            else:
                user_profile.direccion = None  # otros perfiles no tienen dirección asignada

            user_profile.save()

            messages.add_message(request, messages.INFO, "Usuario actualizado correctamente.")
        else:
            # Creación
            if not (username and email and password and group_name):
                messages.add_message(request, messages.INFO, "Faltan datos obligatorios.")
                return redirect("usuario_actualizar")

            if User.objects.filter(username=username).exists():
                messages.add_message(request, messages.INFO, "Usuario ya existe.")
                return redirect("usuario_actualizar")

            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=first_name or '',
                last_name=last_name or ''
            )
            user.set_password(password)
            user.is_active = True
            user.save()

            try:
                group = Group.objects.get(name=group_name)
            except Group.DoesNotExist:
                messages.add_message(request, messages.INFO, "Grupo no válido.")
                return redirect("usuario_actualizar")

            user.groups.add(group)
            direccion = None
            if group.name == "Territorial":
                direccion_id = request.POST.get("direccion_id")
                try:
                    direccion = Direccion.objects.get(pk=direccion_id)
                except Direccion.DoesNotExist:
                    messages.add_message(request, messages.INFO, "Debe seleccionar una dirección válida para el territorial.")
                    return redirect("usuario_actualizar")

            Profile.objects.create(
                user=user,
                group=group,
                telefono=telefono or '',
                direccion=direccion
            )

            messages.add_message(request, messages.INFO, "Usuario creado correctamente.")

        return redirect("usuarios_listar")

    grupos = Group.objects.all()
    return render(request, "administracion/usuarios_actualizar.html", {
        "usuario": user,
        "user_profile": user_profile,
        "grupos": grupos,
        "direcciones": Direccion.objects.filter(esta_activa=True),
        "group_name": profile.group.name
    })


@login_required
def usuario_bloquear(request, user_id):
    # Activar/desactivar usuario
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        messages.add_message(request, messages.INFO, "Error obteniendo perfil.")
        return redirect("logout")

    if profile.group.name != "SECPLA":
        messages.add_message(request, messages.INFO, "No tienes permisos.")
        return redirect("logout")

    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        messages.add_message(request, messages.INFO, "Usuario no encontrado.")
        return redirect("usuarios_listar")

    user.is_active = not user.is_active
    user.save()
    estado = "activado" if user.is_active else "bloqueado"
    messages.add_message(request, messages.INFO, f"Usuario {estado} correctamente.")
    return redirect("usuarios_listar")


@login_required
def usuario_ver(request, user_id):
    # Ver ficha de usuario
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        messages.add_message(request, messages.INFO, "Error obteniendo perfil.")
        return redirect("logout")

    if profile.group.name != "SECPLA":
        messages.add_message(request, messages.INFO, "No tienes permisos.")
        return redirect("logout")

    try:
        user = User.objects.get(pk=user_id)
        user_profile = Profile.objects.get(user=user)
    except (User.DoesNotExist, Profile.DoesNotExist):
        messages.add_message(request, messages.INFO, "Usuario no encontrado.")
        return redirect("usuarios_listar")

    return render(request, "administracion/usuarios_ver.html", {
        "usuario": user,
        "user_profile": user_profile,
        "group_name": profile.group.name
    })
