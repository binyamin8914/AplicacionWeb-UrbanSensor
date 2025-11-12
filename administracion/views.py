from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.db import IntegrityError # Importamos el manejador de errores

from registration.models import Profile
from direcciones.models import Direccion
from departamentos.models import Departamento
from cuadrillas.models import Cuadrilla


# ===================================================================
# --- VISTAS DE USUARIOS ---
# ===================================================================
@login_required
def usuarios_listar(request):
    # (Tu vista de usuarios_listar... está perfecta)
    try:
        profile = Profile.objects.get(user=request.user)
    except:
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
        'titulo': "Gestión de Usuarios", 'descripcion': "Gestión de todos los usuarios de la plataforma",
        'url': {'name': 'usuario_actualizar', 'label': 'Nuevo Usuario', 'ic': ''},
        'titulos': ['Usuario', 'Nombre', 'Apellido', 'Correo', 'Teléfono', 'Perfil', 'Estado'],
        'back': 'dashboard', 'filtros': [
            { 'nombre': 'Estado', 'nombre_corto': 'estado', 'opciones': ["Activo", "Bloqueado"]},
            { 'nombre': 'Perfil', 'nombre_corto': 'perfil', 'opciones': [grupo.name for grupo in grupos_para_filtro]}
        ], 'tieneAcciones': True, "group_name": profile.group.name,
        'current_filtro_estado': filtro_estado, 'current_filtro_perfil': filtro_perfil,
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
                usuario.email, usuario.profile.telefono, usuario.profile.group.name,
                'Activo' if usuario.is_active else 'Bloqueado',  
            ],
            'clases': ['', '', '', '', '', '', 'Activo' if usuario.is_active else 'Inactivo']
        })
    return render(request, "administracion/usuarios_listar.html", datos)

@login_required
def usuario_actualizar(request, user_id=None):
    # (Tu vista de usuario_actualizar... está perfecta)
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
        if user:
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
        else:
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
        "usuario": user, "user_profile": user_profile,
        "grupos": grupos, "group_name": profile.group.name
    })

@login_required
def usuario_bloquear(request, user_id):
    # (Tu vista de usuario_bloquear... está perfecta)
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
    # (Tu vista de usuario_ver... está perfecta)
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
# --- VISTAS DE DIRECCIONES ---
# ===================================================================
@login_required
def direccion_listar(request):
    # (Tu vista de direccion_listar... está perfecta)
    filtro_estado = request.GET.get('estado')
    direcciones = Direccion.objects.all().order_by('nombre')
    if filtro_estado == 'Activo':
        direcciones = direcciones.filter(esta_activa=True)
    elif filtro_estado == 'Inactivo':
        direcciones = direcciones.filter(esta_activa=False)
    context = {
        'titulo': 'Gestión de Direcciones', 'direcciones': direcciones,
        'current_filtro_estado': filtro_estado, "group_name": request.user.profile.group.name,
    }
    return render(request, 'administracion/direccion_listar.html', context)

@login_required
def direccion_actualizar(request, id=None):
    # (Tu vista de direccion_actualizar... está perfecta)
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
            try: 
                if direccion:
                    direccion.nombre = nombre
                    direccion.encargado = encargado
                    direccion.correo_encargado = correo_encargado
                    direccion.save()
                    messages.success(request, "¡Dirección actualizada con éxito!")
                else:
                    Direccion.objects.create(
                        nombre=nombre, encargado=encargado,
                        correo_encargado=correo_encargado, esta_activa=True 
                    )
                    messages.success(request, "¡Dirección creada con éxito!")
                return redirect('direccion_listar')
            except IntegrityError: 
                messages.error(request, f"Error: El usuario '{encargado.username}' ya es encargado de otra dirección. Por favor, seleccione un usuario diferente.")
    try:
        grupo_direccion = Group.objects.get(name="Direccion")
        encargados = User.objects.filter(groups=grupo_direccion)
    except Group.DoesNotExist:
        encargados = User.objects.filter(is_superuser=True) 
    context = {
        'titulo_pagina': titulo_pagina, 'direccion': direccion,
        'encargados': encargados, "group_name": request.user.profile.group.name,
    }
    return render(request, 'administracion/direccion_actualizar.html', context)

@login_required
def direccion_bloquear(request, id):
    # (Tu vista de direccion_bloquear... está perfecta)
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
def direccion_ver(request, id): # <-- VISTA AÑADIDA
    direccion = get_object_or_404(Direccion, id=id)
    context = {
        'direccion': direccion,
        "group_name": request.user.profile.group.name,
    }
    return render(request, 'administracion/direccion_ver.html', context)

# ===================================================================
# --- VISTAS DE DEPARTAMENTOS ---
# ===================================================================
@login_required
def departamento_listar(request):
    # (Tu vista de departamento_listar... está perfecta)
    filtro_estado = request.GET.get('estado')
    departamentos = Departamento.objects.select_related('direccion').all().order_by('nombre')
    if filtro_estado == 'Activo':
        departamentos = departamentos.filter(esta_activo=True)
    elif filtro_estado == 'Inactivo':
        departamentos = departamentos.filter(esta_activo=False)
    context = {
        'titulo': 'Gestión de Departamentos', 'departamentos': departamentos,
        'current_filtro_estado': filtro_estado, "group_name": request.user.profile.group.name,
    }
    return render(request, 'administracion/departamento_listar.html', context)

@login_required
def departamento_actualizar(request, id=None):
    # (Tu vista de departamento_actualizar... está perfecta)
    if id:
        departamento = get_object_or_404(Departamento, id=id)
        titulo_pagina = "Editar Departamento"
    else:
        departamento = None
        titulo_pagina = "Crear Nuevo Departamento"
    if request.method == "POST":
        nombre = request.POST.get('nombre')
        encargado_id = request.POST.get('encargado')
        correo_encargado = request.POST.get('correo_encargado')
        direccion_id = request.POST.get('direccion')
        if not all([nombre, encargado_id, direccion_id]):
            messages.error(request, "Nombre, Encargado y Dirección son obligatorios.")
        else:
            encargado = get_object_or_404(User, id=encargado_id)
            direccion = get_object_or_404(Direccion, id=direccion_id)
            try:
                if departamento:
                    departamento.nombre = nombre
                    departamento.encargado = encargado
                    departamento.correo_encargado = correo_encargado
                    departamento.direccion = direccion
                    departamento.save()
                    messages.success(request, "¡Departamento actualizado con éxito!")
                else:
                    Departamento.objects.create(
                        nombre=nombre, encargado=encargado,
                        correo_encargado=correo_encargado, direccion=direccion,
                        esta_activo=True 
                    )
                    messages.success(request, "¡Departamento creado con éxito!")
                return redirect('departamento_listar')
            except IntegrityError: 
                messages.error(request, f"Error: El usuario '{encargado.username}' ya es encargado de otro departamento. Por favor, seleccione un usuario diferente.")
    try:
        grupo_depto = Group.objects.get(name="Departamento")
        encargados = User.objects.filter(groups=grupo_depto)
    except Group.DoesNotExist:
        encargados = User.objects.filter(is_superuser=True)
    direcciones = Direccion.objects.filter(esta_activa=True)
    context = {
        'titulo_pagina': titulo_pagina, 'departamento': departamento,
        'encargados': encargados, 'direcciones': direcciones,
        "group_name": request.user.profile.group.name,
    }
    return render(request, 'administracion/departamento_actualizar.html', context)

@login_required
def departamento_bloquear(request, id):
    # (Tu vista de departamento_bloquear... está perfecta)
    departamento = get_object_or_404(Departamento, id=id)
    departamento.esta_activo = not departamento.esta_activo
    departamento.save()
    estado = "activado" if departamento.esta_activo else "bloqueado"
    messages.success(request, f"Departamento {estado} correctamente.")
    return redirect('departamento_listar')

@login_required
def departamento_ver(request, id): # <-- VISTA AÑADIDA
    departamento = get_object_or_404(Departamento, id=id)
    context = {
        'departamento': departamento,
        "group_name": request.user.profile.group.name,
    }
    return render(request, 'administracion/departamento_ver.html', context)

# ===================================================================
# --- VISTAS DE CUADRILLAS (¡¡AHORA RELLENAS!!) ---
# ===================================================================

@login_required
def cuadrilla_listar(request):
    # (Tu vista de cuadrilla_listar... está perfecta)
    filtro_estado = request.GET.get('estado')
    filtro_depto = request.GET.get('departamento') # Filtro nuevo
    
    cuadrillas = Cuadrilla.objects.select_related('departamento').all()
    
    if filtro_estado == 'Activo':
        cuadrillas = cuadrillas.filter(esta_activa=True)
    elif filtro_estado == 'Inactivo':
        cuadrillas = cuadrillas.filter(esta_activa=False)
        
    if filtro_depto:
        cuadrillas = cuadrillas.filter(departamento__id=filtro_depto) # Filtro nuevo

    cuadrillas = cuadrillas.order_by('nombre')
    
    context = {
        'titulo': 'Gestión de Cuadrillas',
        'cuadrillas': cuadrillas,
        'departamentos_filtro': Departamento.objects.filter(esta_activo=True),
        'current_filtro_estado': filtro_estado,
        'current_filtro_depto': filtro_depto,
        "group_name": request.user.profile.group.name,
    }
    return render(request, 'administracion/cuadrilla_listar.html', context)


@login_required
def cuadrilla_actualizar(request, id=None):
    # --- ¡¡ESTA ES LA LÓGICA QUE FALTABA!! ---
    if id:
        cuadrilla = get_object_or_404(Cuadrilla, id=id)
        titulo_pagina = "Editar Cuadrilla"
    else:
        cuadrilla = None
        titulo_pagina = "Crear Nueva Cuadrilla"

    if request.method == "POST":
        nombre = request.POST.get('nombre')
        encargado_id = request.POST.get('encargado')
        departamento_id = request.POST.get('departamento')

        if not all([nombre, encargado_id, departamento_id]):
            messages.error(request, "Nombre, Encargado y Departamento son obligatorios.")
        else:
            encargado = get_object_or_404(User, id=encargado_id)
            departamento = get_object_or_404(Departamento, id=departamento_id)
            
            try: # --- ¡¡ATRAPAMOS EL ERROR DE DUPLICADO!! ---
                if cuadrilla:
                    # Actualizar
                    cuadrilla.nombre = nombre
                    cuadrilla.encargado = encargado
                    cuadrilla.departamento = departamento
                    cuadrilla.save()
                    messages.success(request, "¡Cuadrilla actualizada con éxito!")
                else:
                    # Crear
                    Cuadrilla.objects.create(
                        nombre=nombre,
                        encargado=encargado,
                        departamento=departamento,
                        esta_activa=True 
                    )
                    messages.success(request, "¡Cuadrilla creada con éxito!")
                
                return redirect('cuadrilla_listar')

            except IntegrityError: 
                messages.error(request, f"Error: El usuario '{encargado.username}' ya es encargado de otra cuadrilla. Por favor, seleccione un usuario diferente.")
                
    # --- Lógica GET (o si el POST falló) ---
    try:
        grupo_cuadrilla = Group.objects.get(name="Cuadrilla")
        encargados = User.objects.filter(groups=grupo_cuadrilla)
    except Group.DoesNotExist:
        encargados = User.objects.all() # Plan B: mostrar todos
    
    departamentos = Departamento.objects.filter(esta_activo=True)

    context = {
        'titulo_pagina': titulo_pagina,
        'cuadrilla': cuadrilla,
        'encargados': encargados,
        'departamentos': departamentos,
        "group_name": request.user.profile.group.name,
    }
    return render(request, 'administracion/cuadrilla_actualizar.html', context)


@login_required
def cuadrilla_bloquear(request, id):
    # --- LÓGICA RELLENADA ---
    cuadrilla = get_object_or_404(Cuadrilla, id=id)
    cuadrilla.esta_activa = not cuadrilla.esta_activa
    cuadrilla.save()
    estado = "activada" if cuadrilla.esta_activa else "desactivada"
    messages.success(request, f"Cuadrilla {estado} correctamente.")
    return redirect('cuadrilla_listar')

@login_required
def cuadrilla_ver(request, id): # <-- VISTA AÑADIDA
    cuadrilla = get_object_or_404(Cuadrilla, id=id)
    context = {
        'cuadrilla': cuadrilla,
        "group_name": request.user.profile.group.name,
    }
    return render(request, 'administracion/cuadrilla_ver.html', context)