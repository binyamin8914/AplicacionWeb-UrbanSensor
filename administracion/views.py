from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.contrib import messages
from registration.models import Profile
<<<<<<< HEAD
=======
from .models import Direccion, Departamento, Cuadrilla
>>>>>>> dd07e64c90885b997006adea9d8508f590459c99

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
<<<<<<< HEAD
    usuarios_db = User.objects.all().order_by('username')
    datos = {
        'titulo': "Gestión de Usuarios",
        'descripcion': "Gestión de todos los usuarios de la plataforma",
        'url': {'name': 'usuario_actualizar', 'label': 'Nuevo Usuario', 'ic': ''},
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
        'filtros': [{
            'nombre': 'Estado',
            'nombre_corto': 'estado',
            'ic': '󰣕',
            'opciones': ["Activo", "Bloqueado"]
        },
        {
            'nombre': 'Perfil',
            'nombre_corto': 'perfil',
            'ic': '',
            'opciones': [grupo.name for grupo in Group.objects.all()]
        }],
        'tieneAcciones': True,
        "group_name": profile.group.name
    }
    return render(request, "administracion/usuarios_listar.html", datos)
=======
    usuarios = User.objects.all().order_by('username')
    return render(request, "administracion/usuarios_listar.html", {"usuarios": usuarios})
>>>>>>> dd07e64c90885b997006adea9d8508f590459c99

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
<<<<<<< HEAD
            return redirect("usuarios_listar")
=======
            return redirect("administracion:usuarios_listar")
>>>>>>> dd07e64c90885b997006adea9d8508f590459c99
    else:
        user = None
        user_profile = None

    if request.method == "POST":
        username = request.POST.get("username")
<<<<<<< HEAD
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
=======
>>>>>>> dd07e64c90885b997006adea9d8508f590459c99
        email = request.POST.get("email")
        password = request.POST.get("password")
        group_name = request.POST.get("group")
        telefono = request.POST.get("telefono")

        if user:  # Edición
<<<<<<< HEAD
            user.first_name = first_name
            user.last_name = last_name
=======
>>>>>>> dd07e64c90885b997006adea9d8508f590459c99
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
<<<<<<< HEAD
                return redirect("usuario_actualizar")
            if User.objects.filter(username=username).exists():
                messages.add_message(request, messages.INFO, "Usuario ya existe.")
                return redirect("usuario_actualizar")
            user = User.objects.create_user(username=username, email=email, first_name=first_name, last_name=last_name)
=======
                return redirect("administracion]:usuario_actualizar")
            if User.objects.filter(username=username).exists():
                messages.add_message(request, messages.INFO, "Usuario ya existe.")
                return redirect("administracion:usuario_actualizar")
            user = User.objects.create_user(username=username, email=email)
>>>>>>> dd07e64c90885b997006adea9d8508f590459c99
            user.set_password(password)
            user.is_active = True
            user.save()
            group = Group.objects.get(name=group_name)
            user.groups.add(group)
            Profile.objects.create(user=user, group=group, telefono=telefono)
            messages.add_message(request, messages.INFO, "Usuario creado correctamente.")
<<<<<<< HEAD
        return redirect("usuarios_listar")

    grupos = Group.objects.all()
    return render(request, "administracion/usuarios_actualizar.html", {
        "usuario": user,
        "user_profile": user_profile,
        "grupos": grupos,
        "group_name": profile.group.name
=======
        return redirect("administracion:usuarios_listar")

    grupos = Group.objects.all()
    return render(request, "administracion/usuario_actualizar.html", {
        "usuario": user,
        "user_profile": user_profile,
        "grupos": grupos
>>>>>>> dd07e64c90885b997006adea9d8508f590459c99
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
<<<<<<< HEAD
        return redirect("usuarios_listar")
=======
        return redirect("administracion:usuarios_listar")
>>>>>>> dd07e64c90885b997006adea9d8508f590459c99
    user.is_active = not user.is_active
    user.save()
    estado = "activado" if user.is_active else "bloqueado"
    messages.add_message(request, messages.INFO, f"Usuario {estado} correctamente.")
<<<<<<< HEAD
    return redirect("usuarios_listar")
=======
    return redirect("administracion:usuarios_listar")
>>>>>>> dd07e64c90885b997006adea9d8508f590459c99

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
<<<<<<< HEAD
        return redirect("usuarios_listar")
    return render(request, "administracion/usuarios_ver.html", {"usuario": user, "user_profile": user_profile, "group_name": profile.group.name})
=======
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
>>>>>>> dd07e64c90885b997006adea9d8508f590459c99
