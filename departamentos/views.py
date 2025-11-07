from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from registration.models import Profile
from .models import Departamento, Direccion
from incidencias.models import Incidencia
from cuadrillas.models import Cuadrilla
from django.db.models import Count

# --- CRUD Departamento ---

@login_required
def departamento_listar(request):
    profile = Profile.objects.get(user=request.user)
    if profile.group.name not in ["SECPLA", "Direccion"]:
        messages.add_message(request, messages.INFO, "No tienes permisos.")
        return redirect("logout")

    departamentos = Departamento.objects.all().order_by('nombre')
    datos = {
        'titulo': "Gestión de Departamentos",
        'descripcion': "Gestión de todos los departamentos",
        'url': {'name': 'departamento_actualizar', 'label': 'Nuevo Departamento', 'ic': ''},
        'titulos': ['Nombre Departamento', 'Encargado', 'Correo Encargado', 'Dirección', 'Estado'],
        'filas': [{
            "id": departamento.id,
            'acciones': [
                {'url': 'departamento_ver', 'name': 'Ver', 'ic': ''},
                {'url': 'departamento_actualizar', 'name': 'Editar', 'ic': ''},
                {'url': 'departamento_bloquear',
                 'name': 'Bloquear' if departamento.esta_activo else 'Activar',
                 'ic': '' if departamento.esta_activo else ''}
            ],
            "columnas": [
                departamento.nombre,
                departamento.encargado.get_full_name(),
                departamento.correo_encargado,
                departamento.direccion.nombre,
                'Activo' if departamento.esta_activo else 'Bloqueado',
            ],
            'clases': ['', '', '', '', 'Activo' if departamento.esta_activo else 'Inactivo']
        } for departamento in departamentos],
        'filtros': [
            {
                'nombre': 'Estado',
                'nombre_corto': 'estado',
                'ic': '󰣕',
                'opciones': ["Activo", "Bloqueado"]
            },
            {
                'nombre': 'Dirección',
                'nombre_corto': 'direccion',
                'ic': '',
                'opciones': [direccion.nombre for direccion in Direccion.objects.all()]
            }
        ],
        'tieneAcciones': True,
        "group_name": profile.group.name
    }

    return render(request, "departamentos/departamento_listar.html", datos)


@login_required
def departamento_actualizar(request, departamento_id=None):
    profile = Profile.objects.get(user=request.user)
    if profile.group.name not in ["SECPLA", "Direccion"]:
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
    return render(request, "departamentos/departamento_ver.html", {
        "departamento": departamento,
        "group_name": profile.group.name
    })


@login_required
def departamento_bloquear(request, departamento_id):
    profile = Profile.objects.get(user=request.user)
    if profile.group.name not in ["SECPLA", "Direccion"]:
        messages.add_message(request, messages.INFO, "No tienes permisos.")
        return redirect("logout")

    departamento = get_object_or_404(Departamento, pk=departamento_id)
    departamento.esta_activo = not departamento.esta_activo
    departamento.save()
    estado = "activado" if departamento.esta_activo else "bloqueado"
    messages.success(request, f"Departamento {estado} correctamente.")
    return redirect("departamento_listar")


# =======================================================
# VISTAS PARA EL DASHBOARD Y GESTIÓN DE INCIDENCIAS POR DEPARTAMENTO
# =======================================================

@login_required
def departamento_dashboard(request):
    # Solo el encargado del departamento puede ingresar
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        messages.error(request, "Error obteniendo perfil.")
        return redirect("logout")

    # Obtener departamento cuyo encargado es el usuario
    departamento = Departamento.objects.filter(encargado=request.user).first()
    if not departamento:
        messages.info(request, "No eres encargado de ningún departamento.")
        return redirect("logout")

    # Conteo de incidencias por estado para este departamento
    incidencias = Incidencia.objects.filter(encuesta__departamento=departamento)
    estados_count = incidencias.values('estado').annotate(total=Count('id'))

    # Convertir a dict para la plantilla
    counts = {item['estado']: item['total'] for item in estados_count}

    context = {
        "departamento": departamento,
        "counts": counts,
        "group_name": profile.group.name
    }
    return render(request, "departamentos/dashboard_departamento.html", context)

@login_required
def incidencias_por_estado(request, estado=None):
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        messages.error(request, "Error obteniendo perfil.")
        return redirect("logout")

    departamento = Departamento.objects.filter(encargado=request.user).first()
    if not departamento:
        messages.info(request, "No eres encargado de ningún departamento.")
        return redirect("logout")

    if estado:
        incidencias = Incidencia.objects.filter(encuesta__departamento=departamento, estado=estado).order_by('-created_at')
    else:
        incidencias = Incidencia.objects.filter(encuesta__departamento=departamento).order_by('-created_at')

    context = {
        "departamento": departamento,
        "incidencias": incidencias,
        "estado": estado,
        "group_name": profile.group.name
    }
    return render(request, "incidencias/gestion_incidencias.html", context)

@login_required
def incidencia_ver_y_derivar(request, incidencia_id):
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        messages.error(request, "Error obteniendo perfil.")
        return redirect("logout")

    departamento = Departamento.objects.filter(encargado=request.user).first()
    if not departamento:
        messages.info(request, "No eres encargado de ningún departamento.")
        return redirect("logout")

    incidencia = get_object_or_404(Incidencia, pk=incidencia_id, encuesta__departamento=departamento)

    # Cuadrillas disponibles del mismo departamento
    cuadrillas = Cuadrilla.objects.filter(departamento=departamento, esta_activa=True)

    if request.method == "POST":
        cuadrilla_id = request.POST.get("cuadrilla")
        if not cuadrilla_id:
            messages.info(request, "Selecciona una cuadrilla.")
            return redirect("incidencia_ver_y_derivar", incidencia_id=incidencia.id)
        try:
            cuadrilla = Cuadrilla.objects.get(pk=cuadrilla_id)
        except Cuadrilla.DoesNotExist:
            messages.error(request, "Cuadrilla no encontrada.")
            return redirect("incidencia_ver_y_derivar", incidencia_id=incidencia.id)

        # Validar que la cuadrilla pertenezca al mismo departamento
        if cuadrilla.departamento_id != departamento.id:
            messages.error(request, "La cuadrilla seleccionada no pertenece a tu departamento.")
            return redirect("incidencia_ver_y_derivar", incidencia_id=incidencia.id)

        # Asignar y marcar como derivada
        incidencia.cuadrilla = cuadrilla
        incidencia.estado = 'derivada'
        incidencia.save()
        messages.success(request, "Incidencia derivada a cuadrilla correctamente.")
        return redirect("incidencias_por_estado", estado="derivada")

    context = {
        "incidencia": incidencia,
        "cuadrillas": cuadrillas,
        "group_name": profile.group.name
    }
    return render(request, "incidencias/detalle_incidencia.html", context)
