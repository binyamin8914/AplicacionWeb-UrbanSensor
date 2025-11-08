from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.contrib import messages

from registration.models import Profile
# --- IMPORTANTE: Importamos los modelos que vamos a listar ---
from direcciones.models import Direccion
from departamentos.models import Departamento
from cuadrillas.models import Cuadrilla


# ===================================================================
# --- VISTAS DE USUARIOS ---
# ===================================================================

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

    # Lógica de Filtros
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
                {'url': 'usuario_actualizar_id', 'name': 'Editar', 'ic': ''}, # Nombre de URL corregido
                {'url': 'usuario_bloquear', 'name': 'Bloquear' if usuario.is_active else 'Activar', 'ic': '' if usuario.is_active else ''}
            ],
            "columnas": [
                usuario.username, 
                usuario.first_name, 
                usuario.last_name,
                usuario.email, 
                usuario.profile.telefono, 
                usuario.profile.group.name,
                'Activo' if usuario.is_active else 'Bloqueado',  
            ],
            'clases': ['', '', '', '', '', '', 'Activo' if usuario.is_active else 'Inactivo']
        })
        
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


# ===================================================================
# --- VISTAS PARA DIRECCIONES, DEPTOS Y CUADRILLAS ---
# ===================================================================

@login_required
def direccion_listar(request):
    filtro_estado = request.GET.get('estado')
    direcciones = Direccion.objects.all().order_by('nombre')
    
    if filtro_estado == 'Activo':
        direcciones = direcciones.filter(esta_activa=True)
    elif filtro_estado == 'Inactivo':
        direcciones = direcciones.filter(esta_activa=False)

    context = {
        'titulo': 'Gestión de Direcciones',
        'direcciones': direcciones,
        'current_filtro_estado': filtro_estado,
        "group_name": request.user.profile.group.name,
    }
    return render(request, 'administracion/direccion_listar.html', context)

@login_required
def departamento_listar(request):
    filtro_estado = request.GET.get('estado')
    departamentos = Departamento.objects.select_related('direccion').all().order_by('nombre')
    
    if filtro_estado == 'Activo':
        departamentos = departamentos.filter(esta_activo=True)
    elif filtro_estado == 'Inactivo':
        departamentos = departamentos.filter(esta_activo=False)

    context = {
        'titulo': 'Gestión de Departamentos',
        'departamentos': departamentos,
        'current_filtro_estado': filtro_estado,
        "group_name": request.user.profile.group.name,
    }
    return render(request, 'administracion/departamento_listar.html', context)

@login_required
def cuadrilla_listar(request):
    filtro_estado = request.GET.get('estado')
    cuadrillas = Cuadrilla.objects.select_related('departamento').all().order_by('nombre')
    
    if filtro_estado == 'Activo':
        cuadrillas = cuadrillas.filter(esta_activa=True)
    elif filtro_estado == 'Inactivo':
        cuadrillas = cuadrillas.filter(esta_activa=False)

    context = {
        'titulo': 'Gestión de Cuadrillas',
        'cuadrillas': cuadrillas,
        'current_filtro_estado': filtro_estado,
        "group_name": request.user.profile.group.name,
    }
    return render(request, 'administracion/cuadrilla_listar.html', context)


# ===================================================================
# --- VISTAS DE ACCIÓN (Crear/Editar/Bloquear) ---
# ===================================================================

@login_required
def direccion_actualizar(request, id=None):
    if id:
        direccion = get_object_or_404(Direccion, id=id)
        titulo_pagina = "Editar Dirección"
    else:
        direccion = None
        titulo_pagina = "Crear Nueva Dirección"

    if request.method == "POST":
        nombre = request.POST.get('nombre')
        encargado_id = request.POST.get('encargado')
        correo_encargado = request.POST.get('correo_encargado')
        
        if not nombre or not encargado_id:
            messages.error(request, "Nombre y Encargado son obligatorios.")
        else:
            encargado = get_object_or_404(User, id=encargado_id)
            
            if direccion:
                direccion.nombre = nombre
                direccion.encargado = encargado
                direccion.correo_encargado = correo_encargado
                direccion.save()
                messages.success(request, "¡Dirección actualizada con éxito!")
            else:
                Direccion.objects.create(
                    nombre=nombre,
                    encargado=encargado,
                    correo_encargado=correo_encargado,
                    esta_activa=True 
                )
                messages.success(request, "¡Dirección creada con éxito!")
            return redirect('direccion_listar')

    try:
        grupo_direccion = Group.objects.get(name="Direccion")
        encargados = User.objects.filter(groups=grupo_direccion)
    except Group.DoesNotExist:
        encargados = User.objects.filter(is_superuser=True) 

    context = {
        'titulo_pagina': titulo_pagina,
        'direccion': direccion,
        'encargados': encargados,
        "group_name": request.user.profile.group.name,
    }
    return render(request, 'administracion/direccion_actualizar.html', context)


@login_required
def direccion_bloquear(request, id):
    try:
        direccion = get_object_or_404(Direccion, id=id)
        direccion.esta_activa = not direccion.esta_activa 
        direccion.save()
        estado = "activada" if direccion.esta_activa else "desactivada"
        messages.success(request, f"Dirección {estado} correctamente.")
    except Exception as e:
        messages.error(request, f"Error al cambiar el estado: {e}")
    return redirect('direccion_listar')


@login_required
def departamento_actualizar(request, id=None):
    # TODO: Crear el formulario y la lógica para Departamento
    messages.warning(request, "Función 'Actualizar Departamento' aún no implementada.")
    return redirect('departamento_listar')

@login_required
def departamento_bloquear(request, id):
    # TODO: Crear la lógica para bloquear/activar Departamento
    messages.warning(request, "Función 'Bloquear Departamento' aún no implementada.")
    return redirect('departamento_listar')

@login_required
def cuadrilla_actualizar(request, id=None):
    # TODO: Crear el formulario y la lógica para Cuadrilla
    messages.warning(request, "Función 'Actualizar Cuadrilla' aún no implementada.")
    return redirect('cuadrilla_listar')

@login_required
def cuadrilla_bloquear(request, id):
    # TODO: Crear la lógica para bloquear/activar Cuadrilla
    messages.warning(request, "Función 'Bloquear Cuadrilla' aún no implementada.")
    return redirect('cuadrilla_listar')