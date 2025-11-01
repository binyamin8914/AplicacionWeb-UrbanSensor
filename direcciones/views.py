from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.models import User
from registration.models import Profile
from .models import Direccion

# --- CRUD Direccion ---

@login_required
def direccion_listar(request):
    profile = Profile.objects.get(user=request.user)
    if profile.group.name != "SECPLA":
        messages.add_message(request, messages.INFO, "No tienes permisos.")
        return redirect("logout")
    direcciones = Direccion.objects.all().order_by('nombre')
    datos = {
        'titulo': "Gestión de Direcciones",
        'descripcion': "Gestión de todas las direcciones",
        'url': {'name': 'direccion_actualizar', 'label': 'Nueva Dirección', 'ic': ''},
        'titulos': ['Nombre Dirección', 'Encargado', 'Correo Encargado', 'Estado'],
        'filas': [{
                "id": direccion.id,
                'acciones': [{'url': 'direccion_ver', 'name': 'Ver', 'ic': ''},
                    {'url': 'direccion_actualizar','name': 'Editar','ic': ''},
                    {'url': 'direccion_bloquear', 'name': 'Bloquear' if direccion.esta_activa else 'Activar', 'ic': '' if direccion.esta_activa else ''}
                ],
                "columnas": [direccion.nombre, direccion.encargado.get_full_name(), direccion.correo_encargado,
                    'Activo' if direccion.esta_activa else 'Bloqueado',   
                ],
                'clases': ['', '', '', 'Activo' if direccion.esta_activa else 'Inactivo']
            }
            for direccion in direcciones
        ],
        'filtros': [{
            'nombre': 'Estado',
            'nombre_corto': 'estado',
            'ic': '󰣕',
            'opciones': ["Activo", "Bloqueado"]
        }],
        'tieneAcciones': True,
        "group_name": profile.group.name
    }
    return render(request, "direcciones/direccion_listar.html", datos)

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
            return redirect("direccion_listar")
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
        return redirect("direccion_listar")

    encargados = User.objects.all()
    return render(request, "direcciones/direccion_actualizar.html", {
        "direccion": direccion,
        "encargados": encargados,
        "group_name": profile.group.name
    })

@login_required
def direccion_ver(request, direccion_id):
    profile = Profile.objects.get(user=request.user)
    if profile.group.name != "SECPLA":
        messages.add_message(request, messages.INFO, "No tienes permisos.")
        return redirect("logout")
    direccion = get_object_or_404(Direccion, pk=direccion_id)
    return render(request, "direcciones/direccion_ver.html", {"direccion": direccion, "group_name": profile.group.name})

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
    return redirect("direccion_listar")