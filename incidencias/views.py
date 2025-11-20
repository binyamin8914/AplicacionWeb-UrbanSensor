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

    if group_name == "SECPLA":
        # SECPLA ve TODAS las incidencias
        incidencias = (
            Incidencia.objects.all()
            .select_related("encuesta__tipo_incidencia__departamento__direccion")
            .order_by("-created_at")
        )
    elif group_name == "Territorial":
        # Territorial ve solo SUS incidencias
        incidencias = (
            Incidencia.objects
            .select_related("encuesta__tipo_incidencia__departamento__direccion")
            .filter(territorial=request.user)
            .order_by("-created_at")
        )
    elif group_name == "Departamento":
        # Departamento ve incidencias de SU departamento
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
        # Dirección ve incidencias de SU dirección
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
        # Cuadrilla ve incidencias ASIGNADAS a ella
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

    # CONTADORES DE ESTADOS 
    context_counts = {}
    if group_name in ["SECPLA", "Direccion", "Departamento"]:
        # Calculamos contadores basados en el queryset ya filtrado por rol
        # (sin aplicar filtro de estado)
        queryset_completo = incidencias if not estado_q else (
            Incidencia.objects.all().select_related(
                "encuesta__tipo_incidencia__departamento__direccion"
            ) if group_name == "SECPLA" else
            incidencias.model.objects.filter(
                pk__in=incidencias.values_list('pk', flat=True)
            )
        )
        
        # Recalcular sin el filtro de estado
        if group_name == "SECPLA":
            base_qs = Incidencia.objects.all()
        elif group_name == "Direccion":
            direccion = getattr(request.user, "direccion_encargada", None)
            base_qs = Incidencia.objects.filter(
                encuesta__tipo_incidencia__departamento__direccion=direccion
            ) if direccion else Incidencia.objects.none()
        elif group_name == "Departamento":
            departamento = Departamento.objects.filter(encargado=request.user).first()
            base_qs = Incidencia.objects.filter(
                encuesta__tipo_incidencia__departamento=departamento
            ) if departamento else Incidencia.objects.none()
        else:
            base_qs = Incidencia.objects.none()

        context_counts = {
            "count_abiertas": base_qs.filter(estado="abierta").count(),
            "count_derivadas": base_qs.filter(estado="derivada").count(),
            "count_rechazadas": base_qs.filter(estado="rechazada").count(),
            "count_finalizadas": base_qs.filter(estado="finalizada").count(),
            "count_cerradas": base_qs.filter(estado="cerrada").count(),
            "count_total": base_qs.count(),
        }

    context = {
        "incidencias": incidencias,
        "group_name": group_name,
        "estado_filtrado": estado_q,
        **context_counts,
    }
    return render(request, "incidencias/gestion_incidencias.html", context)


# ---------------------------------------------------------------------
# Crear Incidencia
# ---------------------------------------------------------------------
@login_required
def crear_incidencia(request):
    form = IncidenciaForm(user=request.user) 

    if request.method == "POST":
        form = IncidenciaForm(request.POST, user=request.user)

        if form.is_valid():
            incidencia = form.save(commit=False)

            profile = getattr(request.user, "profile", None)
            group_name = profile.group.name if profile and profile.group else None

            if group_name == "Territorial":
                incidencia.territorial = request.user
                incidencia.estado = "abierta"

            incidencia.save()

            messages.success(request, "Incidencia creada correctamente.")
            return redirect("gestion_incidencias")

        else:
            messages.error(request, "Revise los datos del formulario.")

    prioridad_choices = list(form.fields['prioridad'].choices) if 'prioridad' in form.fields else []
    optional_fields = ['vecino', 'territorial', 'cuadrilla', 'estado']

    return render(request, "incidencias/formulario_incidencia.html", {
        "form": form,
        "prioridad_choices": prioridad_choices,
        "group_name": get_group_name(request.user),
        "titulo_pagina": "Crear Incidencia",
        "optional_fields": optional_fields,
    })

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
    incidencia = get_object_or_404(
        Incidencia.objects.select_related(
            "encuesta__tipo_incidencia__departamento",
            "cuadrilla",
        ),
        id=incidencia_id
    )
    profile = Profile.objects.get(user=request.user)
    group_name = profile.group.name

    try:
        departamento = incidencia.encuesta.tipo_incidencia.departamento
    except AttributeError:
        messages.error(
            request,
            "La encuesta asociada a esta incidencia no tiene un departamento configurado.",
        )
        return redirect("gestion_incidencias")

    if group_name != "Departamento" or departamento.encargado != request.user:
        messages.error(request, "No tienes permisos para derivar esta incidencia.")
        return redirect("gestion_incidencias")

    if request.method == "POST":
        cuadrilla_id = request.POST.get("cuadrilla")
        if not cuadrilla_id:
            messages.error(request, "Selecciona una cuadrilla.")
            return redirect("gestion_incidencias")

        cuadrilla = get_object_or_404(Cuadrilla, id=cuadrilla_id)

        incidencia.cuadrilla = cuadrilla
        incidencia.estado = "derivada"
        incidencia.save()
        messages.success(
            request,
            f"Incidencia derivada a la cuadrilla '{cuadrilla.nombre}'."
        )
        return redirect("gestion_incidencias")

    cuadrillas = Cuadrilla.objects.filter(departamento=departamento, esta_activa=True)

    return render(
        request,
        "incidencias/derivar.html",
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
def detalle_incidencia(request, incidencia_id):
    incidencia = get_object_or_404(
        Incidencia.objects.select_related(
            "encuesta__tipo_incidencia__departamento__direccion",
            "territorial",
            "cuadrilla",
        ),
        id=incidencia_id
    )
    return render(request, "incidencias/detalle_incidencia.html", {
        "incidencia": incidencia,
        "group_name": get_group_name(request.user),
    })
