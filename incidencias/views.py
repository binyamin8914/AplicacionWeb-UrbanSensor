from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist

from registration.models import Profile
from cuadrillas.models import Cuadrilla
from departamentos.models import Departamento
from .models import Incidencia
from .forms import IncidenciaForm


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
# Gestión unificada de Incidencias
# ---------------------------------------------------------------------
@login_required
def gestion_incidencias(request):
    profile = Profile.objects.get(user=request.user)
    group_name = profile.group.name

    context_counts = {}

    if group_name == "SECPLA":
        return redirect("secpla_dashboard")

    elif group_name == "Territorial":
        incidencias = (
            Incidencia.objects
            .select_related("encuesta__tipo_incidencia__departamento__direccion")
            .filter(territorial=request.user)
            .order_by("-created_at")
        )

    elif group_name == "Departamento":
        departamento = Departamento.objects.filter(encargado=request.user).first()
        if not departamento:
            incidencias = Incidencia.objects.none()
        else:
            incidencias = (
                Incidencia.objects
                .select_related("encuesta__tipo_incidencia__departamento")
                .filter(encuesta__tipo_incidencia__departamento=departamento)
                .order_by("-created_at")
            )

    elif group_name == "Direccion":
        direccion = getattr(request.user, "direccion_encargada", None)
        if not direccion:
            incidencias = Incidencia.objects.none()
        else:
            incidencias = (
                Incidencia.objects
                .select_related("encuesta__tipo_incidencia__departamento__direccion")
                .filter(encuesta__tipo_incidencia__departamento__direccion=direccion)
                .order_by("-created_at")
            )

    elif group_name == "Cuadrilla":
        cuadrilla = Cuadrilla.objects.filter(encargado=request.user).first()
        if not cuadrilla:
            incidencias = Incidencia.objects.none()
        else:
            incidencias = (
                Incidencia.objects
                .select_related(
                    "encuesta__tipo_incidencia__departamento__direccion",
                    "cuadrilla",
                )
                .filter(cuadrilla=cuadrilla)
                .order_by("-created_at")
            )
    else:
        incidencias = Incidencia.objects.none()

    estado_q = request.GET.get("estado")
    if estado_q:
        incidencias = incidencias.filter(estado=estado_q)

    context = {
        "incidencias": incidencias,
        "group_name": group_name,
        **context_counts,
    }
    return render(request, "incidencias/gestion_incidencias.html", context)


# ---------------------------------------------------------------------
# Crear Incidencia
# ---------------------------------------------------------------------
@login_required
def crear_incidencia(request):
    profile = Profile.objects.get(user=request.user)
    group_name = profile.group.name

    if request.method == "POST":
        form = IncidenciaForm(request.POST, user=request.user)
        if form.is_valid():
            data = form.cleaned_data
            incidencia = Incidencia(
                encuesta=data.get("encuesta"),
                vecino=data.get("vecino"),
                descripcion=data.get("descripcion"),
                latitud=data.get("latitud"),
                longitud=data.get("longitud"),
                direccion_textual=data.get("direccion_textual"),
            )
            if group_name == "Territorial":
                incidencia.territorial = request.user
                incidencia.estado = "abierta"
                incidencia.cuadrilla = None
            else:
                incidencia.territorial = data.get("territorial") or None
                incidencia.cuadrilla = data.get("cuadrilla") or None
                incidencia.estado = data.get("estado") or "abierta"

            incidencia.save()
            messages.success(request, "Incidencia creada exitosamente.")
            return redirect("gestion_incidencias")
    else:
        form = IncidenciaForm(user=request.user)

    return render(
        request,
        "incidencias/formulario_incidencia.html",
        {
            "form": form,
            "titulo_pagina": "Crear Incidencia",
            "group_name": group_name,
        },
    )


# ---------------------------------------------------------------------
# Editar Incidencia
# ---------------------------------------------------------------------
@login_required
def editar_incidencia(request, incidencia_id):
    incidencia = get_object_or_404(Incidencia, id=incidencia_id)
    profile = Profile.objects.get(user=request.user)
    group_name = profile.group.name

    if group_name == "Territorial" and incidencia.territorial != request.user:
        messages.error(request, "No tienes permisos para editar esta incidencia.")
        return redirect("gestion_incidencias")

    if group_name == "Cuadrilla":
        messages.error(request, "No tienes permisos para editar incidencias.")
        return redirect("gestion_incidencias")

    if request.method == "POST":
        form = IncidenciaForm(request.POST, user=request.user)
        if form.is_valid():
            datos = form.cleaned_data
            incidencia.encuesta = datos.get("encuesta")
            incidencia.vecino = datos.get("vecino")
            incidencia.descripcion = datos.get("descripcion")
            incidencia.latitud = datos.get("latitud")
            incidencia.longitud = datos.get("longitud")
            incidencia.direccion_textual = datos.get("direccion_textual")

            if group_name != "Territorial":
                incidencia.cuadrilla = datos.get("cuadrilla") or None
                incidencia.estado = datos.get("estado") or incidencia.estado
                incidencia.territorial = datos.get("territorial") or incidencia.territorial
            else:
                incidencia.territorial = request.user

            incidencia.save()
            messages.success(request, "Incidencia actualizada.")
            return redirect("gestion_incidencias")
    else:
        try:
            cuadrilla_obj = incidencia.cuadrilla
        except ObjectDoesNotExist:
            cuadrilla_obj = None

        initial = {
            "encuesta": incidencia.encuesta,
            "vecino": incidencia.vecino,
            "territorial": incidencia.territorial,
            "cuadrilla": cuadrilla_obj.id if cuadrilla_obj else None,
            "descripcion": incidencia.descripcion,
            "latitud": incidencia.latitud,
            "longitud": incidencia.longitud,
            "direccion_textual": incidencia.direccion_textual,
            "estado": incidencia.estado,
        }
        form = IncidenciaForm(initial=initial, user=request.user)

    return render(
        request,
        "incidencias/formulario_incidencia.html",
        {
            "form": form,
            "titulo_pagina": "Editar Incidencia",
            "group_name": group_name,
            "incidencia": incidencia,
        },
    )


# ---------------------------------------------------------------------
# Finalizar Incidencia (Cuadrilla)
# ---------------------------------------------------------------------
@login_required
def finalizar_incidencia(request, incidencia_id):
    incidencia = get_object_or_404(Incidencia, id=incidencia_id)
    profile = Profile.objects.get(user=request.user)
    group_name = profile.group.name

    if group_name != "Cuadrilla":
        messages.error(request, "No tienes permisos para finalizar esta incidencia.")
        return redirect("gestion_incidencias")

    # acceder de forma segura
    cuadrilla = getattr(incidencia, "cuadrilla", None)
    if not cuadrilla or getattr(cuadrilla, "encargado", None) != request.user:
        messages.error(request, "No perteneces a la cuadrilla asignada.")
        return redirect("gestion_incidencias")

    if request.method == "POST":
        incidencia.estado = "finalizada"
        incidencia.save()
        messages.success(request, "Incidencia marcada como finalizada.")
    return redirect("gestion_incidencias")


# ---------------------------------------------------------------------
# Eliminar Incidencia
# ---------------------------------------------------------------------
@login_required
def eliminar_incidencia(request, incidencia_id):
    incidencia = get_object_or_404(Incidencia, id=incidencia_id)
    profile = Profile.objects.get(user=request.user)
    group_name = profile.group.name

    if group_name == "Territorial" and incidencia.territorial != request.user:
        messages.error(request, "No puedes eliminar una incidencia que no creaste.")
        return redirect("gestion_incidencias")

    if request.method == "POST":
        incidencia.delete()
        messages.success(request, "Incidencia eliminada.")
        return redirect("gestion_incidencias")

    return render(
        request,
        "incidencias/confirmar_eliminar_incidencia.html",
        {
            "objeto": incidencia,
            "titulo_objeto": "Incidencia",
            "group_name": group_name,
        },
    )


# ---------------------------------------------------------------------
# Derivar Incidencia (Departamento) -> asigna cuadrilla y marca 'derivada'
# ---------------------------------------------------------------------
@login_required
def derivar_incidencia(request, incidencia_id):
    incidencia = get_object_or_404(Incidencia, id=incidencia_id)
    profile = Profile.objects.get(user=request.user)
    group_name = profile.group.name

    # AQUÍ ESTABA EL ERROR: Encuesta no tiene 'departamento'.
    # Lo correcto es pasar por tipo_incidencia:
    #   encuesta -> tipo_incidencia -> departamento
    try:
        departamento = incidencia.encuesta.tipo_incidencia.departamento
    except AttributeError:
        messages.error(
            request,
            "La encuesta asociada a esta incidencia no tiene un departamento configurado.",
        )
        return redirect("gestion_incidencias")

    # Solo el encargado del departamento puede derivar
    if group_name != "Departamento" or departamento.encargado != request.user:
        messages.error(request, "No tienes permisos para derivar esta incidencia.")
        return redirect("gestion_incidencias")

    if request.method == "POST":
        cuadrilla_id = request.POST.get("cuadrilla")
        if not cuadrilla_id:
            messages.error(request, "Selecciona una cuadrilla.")
            return redirect("gestion_incidencias")

        cuadrilla = get_object_or_404(Cuadrilla, id=cuadrilla_id)

        if cuadrilla.departamento_id != departamento.id:
            messages.error(
                request,
                "La cuadrilla seleccionada no pertenece a este departamento.",
            )
            return redirect("gestion_incidencias")

        incidencia.cuadrilla = cuadrilla
        incidencia.estado = "derivada"
        incidencia.save()
        messages.success(request, "Incidencia derivada a cuadrilla correctamente.")
        return redirect("gestion_incidencias")

    cuadrillas = Cuadrilla.objects.filter(departamento=departamento, esta_activa=True)

    return render(
        request,
        "incidencias/derivar.html",  # o 'incidencias/derivar_incidencia.html' si así se llama tu template
        {
            "incidencia": incidencia,
            "cuadrillas": cuadrillas,
            "group_name": group_name,
        },
    )


# ---------------------------------------------------------------------
# Endpoints JSON para dashboards
# ---------------------------------------------------------------------
@login_required
def territorial_dashboard_data(request):
    profile = Profile.objects.get(user=request.user)
    if profile.group.name != "Territorial":
        return JsonResponse({"error": "forbidden"}, status=403)

    user = request.user
    abiertas = Incidencia.objects.filter(territorial=user, estado="abierta").count()
    derivadas = Incidencia.objects.filter(territorial=user, estado="derivada").count()
    rechazadas = Incidencia.objects.filter(territorial=user, estado="rechazada").count()
    finalizadas = Incidencia.objects.filter(territorial=user, estado="finalizada").count()

    tipos_qs = (
        Incidencia.objects
        .filter(territorial=user)
        .values("encuesta__tipo_incidencia__nombre")
        .annotate(total=Count("id"))
    )
    tipos = [
        {"tipo": i["encuesta__tipo_incidencia__nombre"], "total": i["total"]}
        for i in tipos_qs
    ]

    return JsonResponse(
        {
            "abiertas": abiertas,
            "derivadas": derivadas,
            "rechazadas": rechazadas,
            "finalizadas": finalizadas,
            "tipos": tipos,
        }
    )


@login_required
def secpla_dashboard(request):
    """
    Dashboard para el perfil SECPLA: Muestra conteo de incidencias por estado.
    """
    profile = get_object_or_404(Profile, user=request.user)
    group_name_upper = profile.group.name.upper()

    if group_name_upper != "SECPLA":
        messages.error(
            request,
            "Acceso denegado: Solo SECPLA puede ver este dashboard.",
        )
        return redirect("gestion_incidencias")

    all_incidencias = Incidencia.objects.all()

    context = {
        "total_creadas": all_incidencias.count(),
        "count_derivadas": all_incidencias.filter(estado="derivada").count(),
        "count_rechazadas": all_incidencias.filter(estado="rechazada").count(),
        "count_finalizadas": all_incidencias.filter(estado="finalizada").count(),
        "group_name": profile.group.name,
    }

    return render(request, "incidencias/secpla_dashboard.html", context)


@login_required
def secpla_incidencias_list(request, status=None):
    profile = get_object_or_404(Profile, user=request.user)
    group_name_upper = profile.group.name.upper()

    if group_name_upper != "SECPLA":
        messages.error(request, "Acceso denegado.")
        return redirect("gestion_incidencias")

    queryset = (
        Incidencia.objects
        .select_related(
            "encuesta",
            "encuesta__tipo_incidencia",
            "encuesta__tipo_incidencia__departamento",
            "encuesta__tipo_incidencia__departamento__direccion",
        )
        .order_by("-id")
    )

    if status and status != "todas":
        incidencias = queryset.filter(estado=status)
        title = f"Listado: Incidencias '{status.capitalize()}'"
    else:
        incidencias = queryset.all()
        title = "Listado: Todas las Incidencias Creadas"

    context = {
        "incidencias": incidencias,
        "title": title,
        "group_name": profile.group.name,
        "current_status": status or "todas",
    }
    return render(request, "incidencias/secpla_incidencias_list.html", context)


@login_required
def detalle_incidencia(request, incidencia_id):
    incidencia = get_object_or_404(Incidencia, id=incidencia_id)
    return render(request, "incidencias/detalle_incidencia.html", {"incidencia": incidencia})
