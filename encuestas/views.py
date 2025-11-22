from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction  # Protegemos la BD
from django.db import IntegrityError

from registration.models import Profile
from .models import Encuesta, TipoIncidencia
from .forms import EncuestaForm, CamposAdicionalesFormSet, TipoIncidenciaForm


# ---------------------------------------------------------------------
# Helpers de rol / permiso
# ---------------------------------------------------------------------
def get_group_name(user):
    try:
        return user.profile.group.name
    except Exception:
        return None

def is_secpla(user):
    return get_group_name(user) == "SECPLA"

def is_territorial(user):
    return get_group_name(user) == "Territorial"

def is_departamento(user):
    return get_group_name(user) == "Departamento"

def is_direccion(user):
    return get_group_name(user) == "Direccion"

def is_cuadrilla(user):
    return get_group_name(user) == "Cuadrilla"


# ---------------------------------------------------------------------
# Tipos de Incidencia (SECPLA y Direccion pueden crear/editar/eliminar)
# ---------------------------------------------------------------------
@login_required
def listar_tipos_incidencia(request):
    # Obtener el parámetro de filtro del GET
    filtro_depto_id = request.GET.get("depto_id")

    # Obtener el queryset base de TipoIncidencia
    tipos = (
        TipoIncidencia.objects
        .select_related("departamento")
        .all()
    )
    # Aplicar el filtro si está presente
    if filtro_depto_id:
        try:
            # Filtra por la ID del departamento seleccionado
            tipos = tipos.filter(departamento__id=filtro_depto_id)
        except ValueError:
            # Manejar si el depto_id no es un entero válido
            pass

    # Aplicar el ordenamiento final
    tipos = tipos.order_by("nombre")
    
    # Obtener todos los departamentos para el menú desplegable del filtro
    try:
        from departamentos.models import Departamento
        departamentos_disponibles = Departamento.objects.all().order_by('nombre')
    except ImportError:
        # En caso de que el modelo Departamento no esté importado o disponible
        departamentos_disponibles = []
    
    # Intentar obtener el nombre del departamento filtrado (para mostrar en el botón)
    filtro_depto_nombre = None
    if filtro_depto_id and departamentos_disponibles:
        try:
            depto_obj = departamentos_disponibles.get(id=filtro_depto_id)
            filtro_depto_nombre = depto_obj.nombre
        except Departamento.DoesNotExist:
            pass

    return render(request, "encuestas/listar_tipos_incidencia.html", {
        "tipos": tipos,
        "departamentos": departamentos_disponibles, 
        "filtro_depto_id": filtro_depto_id,   
        "filtro_depto_nombre": filtro_depto_nombre,  
        "group_name": get_group_name(request.user),
    })


@login_required
def crear_tipo_incidencia(request):
    if not (is_secpla(request.user) or is_direccion(request.user)):
        messages.error(request, "No tienes permisos para crear tipos de incidencia.")
        return redirect("listar_tipos_incidencia")

    if request.method == "POST":
        form = TipoIncidenciaForm(request.POST)
        if form.is_valid():
            datos = form.cleaned_data
            TipoIncidencia.objects.create(
                nombre=datos["nombre"],
                descripcion=datos["descripcion"],
                departamento=datos["departamento"],
            )
            messages.success(request, "Tipo de incidencia creado exitosamente.")
            return redirect("listar_tipos_incidencia")
    else:
        form = TipoIncidenciaForm()

    return render(request, "encuestas/crear_tipo_incidencia.html", {
        "form": form,
        "titulo_pagina": "Crear Tipo de Incidencia",
        "group_name": get_group_name(request.user),
    })


@login_required
def editar_tipo_incidencia(request, tipo_id):
    tipo = get_object_or_404(TipoIncidencia, id=tipo_id)

    if not (is_secpla(request.user) or is_direccion(request.user)):
        messages.error(request, "No tienes permisos para editar tipos de incidencia.")
        return redirect("listar_tipos_incidencia")

    if request.method == "POST":
        form = TipoIncidenciaForm(request.POST)
        if form.is_valid():
            datos = form.cleaned_data
            tipo.nombre = datos["nombre"]
            tipo.descripcion = datos["descripcion"]
            tipo.departamento = datos["departamento"]
            tipo.save()
            messages.success(request, "Tipo de incidencia actualizado.")
            return redirect("listar_tipos_incidencia")
    else:
        form = TipoIncidenciaForm(initial={
            "nombre": tipo.nombre,
            "descripcion": tipo.descripcion,
            "departamento": tipo.departamento,
        })

    return render(request, "encuestas/crear_tipo_incidencia.html", {
        "form": form,
        "titulo_pagina": "Editar Tipo de Incidencia",
        "group_name": get_group_name(request.user),
    })


@login_required
def eliminar_tipo_incidencia(request, tipo_id):
    tipo = get_object_or_404(TipoIncidencia, id=tipo_id)

    if not (is_secpla(request.user) or is_direccion(request.user)):
        messages.error(request, "No tienes permisos para eliminar tipos de incidencia.")
        return redirect("listar_tipos_incidencia")

    if request.method == "POST":
        tipo.delete()
        messages.success(request, "Tipo de incidencia eliminado.")
        return redirect("listar_tipos_incidencia")

    return render(request, "encuestas/confirmar_eliminar.html", {
        "objeto": tipo,
        "titulo_objeto": "Tipo de Incidencia",
        "group_name": get_group_name(request.user),
    })


# ---------------------------------------------------------------------
# Gestión de Encuestas
# ---------------------------------------------------------------------
@login_required
def gestion_encuestas(request):
    """
    Lista de encuestas con carga eficiente y paginación.
    SECPLA las crea; otros perfiles (Territorial, etc.) solo las ven/usan.
    """
    profile = Profile.objects.get(user=request.user)

    qs = (
        Encuesta.objects
        .select_related("tipo_incidencia")
        .order_by("-id")
    )

    estado = request.GET.get("estado")

    if estado:
        qs = qs.filter(estado=estado)

    page_obj = Paginator(qs, 10).get_page(request.GET.get("page"))

    # Flag para el template: ¿este usuario es SECPLA?
    es_secpla = is_secpla(request.user)

    return render(request, "encuestas/gestion_encuestas.html", {
        "encuestas": page_obj,
        "f_estado": estado or "",
        "group_name": profile.group.name,
        "es_secpla": es_secpla,  # usado para mostrar/ocultar botón Crear
    })


@login_required
@transaction.atomic
def crear_encuesta(request):
    """
    Crear una encuesta nueva JUNTO con sus campos adicionales.
    Solo SECPLA puede crear encuestas.
    """
    profile = Profile.objects.get(user=request.user)

    # Bloquear a cualquiera que no sea SECPLA
    if not is_secpla(request.user):
        messages.error(request, "No tienes permisos para crear encuestas.")
        return redirect("gestion_encuestas")

    if request.method == "POST":
        form = EncuestaForm(request.POST)
        formset = CamposAdicionalesFormSet(request.POST, prefix="campos")

        if form.is_valid():
            # 1. Guardamos el padre en memoria
            encuesta = form.save(commit=False)

            # 2. Conectamos el formset con el padre
            formset.instance = encuesta

            # 3. Validamos formset
            if formset.is_valid():

                # 4. Guardamos el padre en la BD
                encuesta.save()

                # 5. Guardamos los campos adicionales, asignando orden
                campos = formset.save(commit=False)
                orden_count = 1
                for campo in campos:
                    campo.orden = orden_count
                    campo.save()
                    orden_count += 1

                messages.success(request, "¡La encuesta ha sido creada exitosamente!")
                return redirect("gestion_encuestas")
            else:
                messages.error(request, "Revisa los campos adicionales, hay errores.")
        else:
            messages.error(request, "Revisa los campos principales, hay errores.")

    else:  # GET
        form = EncuestaForm()
        formset = CamposAdicionalesFormSet(prefix="campos")

    return render(request, "encuestas/formulario_encuesta.html", {
        "form": form,
        "formset": formset,
        "titulo_pagina": "Crear Nueva Encuesta",
        "modo": "crear",
        "group_name": profile.group.name,
    })


@login_required
@transaction.atomic
def editar_encuesta(request, encuesta_id: int):
    """
    Editar encuesta existente Y sus campos adicionales.
    Puede editarse si está en estado 'creado' o 'bloqueado'
    """
    profile = Profile.objects.get(user=request.user)
    encuesta_obj = get_object_or_404(Encuesta, id=encuesta_id)

    # Permitir edición solo si está creado o bloqueado
    if encuesta_obj.estado not in ["creado", "bloqueado"]:
        messages.warning(
            request,
            "Solo puedes editar encuestas en estado CREADO o BLOQUEADO.",
        )
        return redirect("gestion_encuestas")

    if request.method == "POST":
        form = EncuestaForm(request.POST, instance=encuesta_obj)
        formset = CamposAdicionalesFormSet(
            request.POST,
            instance=encuesta_obj,
            prefix="campos",
        )

        if form.is_valid() and formset.is_valid():
            form.save()
            campos = formset.save(commit=False)

            orden_count = 1
            for campo in campos:
                campo.orden = orden_count
                campo.save()
                orden_count += 1

            formset.save_m2m()

            messages.success(request, "¡La encuesta ha sido actualizada exitosamente!")
            return redirect("gestion_encuestas")
        else:
            messages.error(
                request,
                "Revisa los campos: hay errores en el formulario.",
            )

    else:
        form = EncuestaForm(instance=encuesta_obj)
        formset = CamposAdicionalesFormSet(
            instance=encuesta_obj,
            prefix="campos",
        )

    return render(request, "encuestas/formulario_encuesta.html", {
        "form": form,
        "formset": formset,
        "titulo_pagina": "Editar Encuesta",
        "modo": "editar",
        "encuesta": encuesta_obj,
        "group_name": profile.group.name,
    })


@login_required
def eliminar_encuesta(request, encuesta_id: int):
    """
    Confirmar y eliminar una encuesta.
    """
    profile = Profile.objects.get(user=request.user)
    encuesta_obj = get_object_or_404(Encuesta, id=encuesta_id)

    if request.method == "POST":
        encuesta_obj.delete()
        messages.success(request, "¡La encuesta ha sido eliminada!")
        return redirect("gestion_encuestas")

    return render(request, "encuestas/confirmar_eliminar_encuesta.html", {
        "encuesta": encuesta_obj,
        "group_name": profile.group.name,
    })


@login_required
def cambiar_estado_encuesta(request, encuesta_id: int):
    """
    Cambia el estado de una encuesta:
    - creado   → vigente   (Activar)
    - vigente  → bloqueado (Bloquear para editar)
    - bloqueado → vigente  (Desbloquear)
    """
    profile = Profile.objects.get(user=request.user)
    encuesta_obj = get_object_or_404(Encuesta, id=encuesta_id)

    if request.method == "POST":
        if encuesta_obj.estado == "creado":
            encuesta_obj.estado = "vigente"
            messages.success(
                request,
                f'La encuesta "{encuesta_obj.titulo}" ha sido ACTIVADA y ya está disponible para usar.',
            )
        elif encuesta_obj.estado == "vigente":
            encuesta_obj.estado = "bloqueado"
            messages.success(
                request,
                f'La encuesta "{encuesta_obj.titulo}" ha sido BLOQUEADA y ahora puede editarse.',
            )
        elif encuesta_obj.estado == "bloqueado":
            encuesta_obj.estado = "vigente"
            messages.success(
                request,
                f'La encuesta "{encuesta_obj.titulo}" ha sido DESBLOQUEADA y está vigente nuevamente.',
            )

        encuesta_obj.save()
        return redirect("gestion_encuestas")

    return render(request, "encuestas/confirmar_cambio_estado.html", {
        "encuesta": encuesta_obj,
        "group_name": profile.group.name,
    })