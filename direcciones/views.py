from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group # Añadimos Group
from django.contrib import messages
from registration.models import Profile
from .models import Direccion

# --- ¡¡IMPORTANTE: Importa el manejador de errores!! ---
from django.db import IntegrityError 

# --- CRUD Direccion ---

@login_required
def direccion_listar(request):
    profile = Profile.objects.get(user=request.user)
    if profile.group.name != "SECPLA":
        messages.add_message(request, messages.INFO, "No tienes permisos.")
        return redirect("logout")
    
    # --- Añadimos la lógica de FILTRO que faltaba ---
    filtro_estado = request.GET.get('estado')
    direcciones = Direccion.objects.all()

    if filtro_estado == 'Activo':
        direcciones = direcciones.filter(esta_activa=True)
    elif filtro_estado == 'Inactivo':
        direcciones = direcciones.filter(esta_activa=False)

    direcciones = direcciones.order_by('nombre')
    
    # --- Reemplazamos 'datos' por 'context' para Bootstrap ---
    context = {
        'titulo': 'Gestión de Direcciones',
        'direcciones': direcciones,
        'current_filtro_estado': filtro_estado,
        "group_name": profile.group.name,
    }
    # Asegúrate de que esta plantilla exista y use Bootstrap
    return render(request, "direcciones/direccion_listar.html", context)

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
            
            # --- ¡¡AQUÍ ESTÁ EL CÓDIGO CLAVE!! ---
            try: 
                if direccion:
                    # Actualizar
                    direccion.nombre = nombre
                    direccion.encargado = encargado
                    direccion.correo_encargado = correo_encargado
                    direccion.save()
                    messages.success(request, "¡Dirección actualizada con éxito!")
                else:
                    # Crear
                    Direccion.objects.create(
                        nombre=nombre,
                        encargado=encargado,
                        correo_encargado=correo_encargado,
                        esta_activa=True 
                    )
                    messages.success(request, "¡Dirección creada con éxito!")
                
                return redirect('direccion_listar') # Solo redirige si todo salió bien

            except IntegrityError: 
                # ¡Atrapamos el error de llave duplicada!
                messages.error(request, f"Error: El usuario '{encargado.username}' ya es encargado de otra dirección. Por favor, seleccione un usuario diferente.")
                # No redirigimos, dejamos que la vista continúe para
                # volver a mostrar el formulario con el mensaje de error.
            # --- FIN DEL BLOQUE TRY/EXCEPT ---

    # --- Lógica GET (o si el POST falló) ---
    try:
        grupo_direccion = Group.objects.get(name="Direccion")
        encargados = User.objects.filter(groups=grupo_direccion)
    except Group.DoesNotExist:
        encargados = User.objects.filter(is_superuser=True) # Plan B

    context = {
        'titulo_pagina': titulo_pagina,
        'direccion': direccion,
        'encargados': encargados,
        "group_name": request.user.profile.group.name,
    }
    # Esta es la plantilla que encontramos que sí funciona
    return render(request, 'administracion/direccion_actualizar.html', context) 

@login_required
def direccion_ver(request, direccion_id):
    # (Tu vista original está bien, la dejamos)
    profile = Profile.objects.get(user=request.user)
    if profile.group.name != "SECPLA":
        messages.add_message(request, messages.INFO, "No tienes permisos.")
        return redirect("logout")
    direccion = get_object_or_404(Direccion, pk=direccion_id)
    return render(request, "direcciones/direccion_ver.html", {"direccion": direccion, "group_name": profile.group.name})


@login_required
def direccion_bloquear(request, direccion_id):
    # (Tu vista original está bien, la dejamos)
    profile = Profile.objects.get(user=request.user)
    if profile.group.name != "SECPLA":
        messages.add_message(request, messages.INFO, "No tienes permisos.")
        return redirect("logout")
    direccion = get_object_or_404(Direccion, pk=direccion_id)
    direccion.esta_activa = not direccion.esta_activa
    direccion.save()
    estado = "activada" if direccion.esta_activa else "bloqueada"
    messages.success(request, f"Dirección {estado} correctamente.")
    return redirect("direccion_listar")