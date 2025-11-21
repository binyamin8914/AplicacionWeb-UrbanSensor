from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist

from registration.models import Profile
from cuadrillas.models import Cuadrilla
from departamentos.models import Departamento
from .models import Incidencia, EncuestaRespuesta
from .forms import IncidenciaForm
from encuestas.models import CamposAdicionales


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
    
@login_required
def api_campos_encuesta(request, encuesta_id):
    campos = list(
        CamposAdicionales.objects.filter(encuesta_id=encuesta_id)
        .values("id", "titulo", "es_obligatoria")
    )
    return JsonResponse({"campos": campos})


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
    profile = Profile.objects.get(user=request.user)
    group_name = profile.group.name

    campos_adicionales = []
    respuestas_prefill = {}

    if request.method == "POST":
        form = IncidenciaForm(request.POST, user=request.user)

        encuesta_id = request.POST.get("encuesta")
        if encuesta_id:
            campos_adicionales = list(CamposAdicionales.objects.filter(encuesta_id=encuesta_id))

        # Prefill con lo enviado (para re-render si hay errores)
        for campo in campos_adicionales:
            respuestas_prefill[campo.id] = request.POST.get(f"campo_{campo.id}", "")

        # Pasamos .valor a cada campo para que template lo use sin filtros
        for campo in campos_adicionales:
            campo.valor = respuestas_prefill.get(campo.id, "")

        # DEBUG: ver estado del campo prioridad y campos adicionales
        print("DEBUG crear_incidencia: campos_adicionales ids =", [c.id for c in campos_adicionales])
        print("DEBUG crear_incidencia: prioridad in form.fields?", 'prioridad' in form.fields)
        if 'prioridad' in form.fields:
            print(" DEBUG prioridad.choices:", form.fields['prioridad'].choices)
            print(" DEBUG prioridad.widget:", type(form.fields['prioridad'].widget))

        if form.is_valid():
            # validar obligatorios de campos adicionales
            missing = [c.titulo for c in campos_adicionales if c.es_obligatoria and not (request.POST.get(f"campo_{c.id}", "") or "").strip()]
            if missing:
                form.add_error(None, "Faltan campos obligatorios: " + ", ".join(missing))
                messages.error(request, "Revisa los campos adicionales obligatorios.")
            else:
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

                # Guardar respuestas a campos adicionales
                respuestas_objs = []
                for campo in campos_adicionales:
                    valor = (request.POST.get(f"campo_{campo.id}", "") or "").strip()
                    if valor != "":
                        respuestas_objs.append(
                            EncuestaRespuesta(incidencia=incidencia, pregunta=campo, valor=valor)
                        )
                if respuestas_objs:
                    EncuestaRespuesta.objects.bulk_create(respuestas_objs)

                messages.success(request, "Incidencia creada exitosamente.")
                return redirect("gestion_incidencias")
        else:
            messages.error(request, "Revise los datos del formulario.")

    else:
        form = IncidenciaForm(user=request.user)

    # si el form ya trae prioridad y quieres render manual, puedes pasar choices:
    prioridad_choices = list(form.fields['prioridad'].choices) if 'prioridad' in form.fields else []

    return render(request, "incidencias/formulario_incidencia.html", {
        "form": form,
        "titulo_pagina": "Crear Incidencia",
        "group_name": group_name,
        "campos_adicionales": campos_adicionales,
        "respuestas_prefill": respuestas_prefill,
        "prioridad_choices": prioridad_choices,
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

    # campos de la encuesta actual y prefills
    campos_adicionales = list(CamposAdicionales.objects.filter(encuesta=incidencia.encuesta))
    respuestas_previas_qs = EncuestaRespuesta.objects.filter(incidencia=incidencia)
    respuestas_prefill = {r.pregunta_id: r.valor for r in respuestas_previas_qs}
    for campo in campos_adicionales:
        campo.valor = respuestas_prefill.get(campo.id, "")

    if request.method == "POST":
        form = IncidenciaForm(request.POST, user=request.user)
        encuesta_id = request.POST.get("encuesta") or (incidencia.encuesta.id if incidencia.encuesta else None)
        # si cambio encuesta, recargar campos basados en la nueva encuesta seleccionada
        if encuesta_id:
            campos_adicionales = list(CamposAdicionales.objects.filter(encuesta_id=encuesta_id))
            for campo in campos_adicionales:
                campo.valor = request.POST.get(f"campo_{campo.id}", "")

        prioridad_choices = list(form.fields['prioridad'].choices) if 'prioridad' in form.fields else []

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

            # validar campos adicionales obligatorios
            campos_post = list(CamposAdicionales.objects.filter(encuesta_id=encuesta_id))
            missing = []
            for campo in campos_post:
                val = (request.POST.get(f"campo_{campo.id}", "") or "").strip()
                if campo.es_obligatoria and not val:
                    missing.append(campo.titulo)

            if missing:
                form.add_error(None, "Faltan campos obligatorios: " + ", ".join(missing))
                messages.error(request, "Revisa los campos adicionales obligatorios.")
            else:
                incidencia.save()
                # renovar respuestas
                EncuestaRespuesta.objects.filter(incidencia=incidencia).delete()
                respuestas_objs = []
                for campo in campos_post:
                    valor = (request.POST.get(f"campo_{campo.id}", "") or "").strip()
                    if valor != "":
                        respuestas_objs.append(
                            EncuestaRespuesta(incidencia=incidencia, pregunta=campo, valor=valor)
                        )
                if respuestas_objs:
                    EncuestaRespuesta.objects.bulk_create(respuestas_objs)

                messages.success(request, "Incidencia actualizada.")
                return redirect("gestion_incidencias")
        else:
            messages.error(request, "Revisa los datos del formulario.")
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
        prioridad_choices = list(form.fields['prioridad'].choices) if 'prioridad' in form.fields else []

    return render(request, "incidencias/formulario_incidencia.html", {
        "form": form,
        "titulo_pagina": "Editar Incidencia",
        "group_name": group_name,
        "incidencia": incidencia,
        "campos_adicionales": campos_adicionales,
        "prioridad_choices": prioridad_choices,
    })


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
            "cuadrilla",
            "territorial",
        ),
        id=incidencia_id
    )

    campos = list(CamposAdicionales.objects.filter(encuesta=incidencia.encuesta).order_by("orden"))
    respuestas_qs = EncuestaRespuesta.objects.filter(incidencia=incidencia).select_related("pregunta")
    respuestas_map = {r.pregunta_id: r.valor for r in respuestas_qs}

    campos_display = []
    for c in campos:
        campos_display.append({
            "id": c.id,
            "titulo": c.titulo,
            "es_obligatoria": c.es_obligatoria,
            "valor": respuestas_map.get(c.id),  # None si no respondido
        })

    context = {
        "incidencia": incidencia,
        "campos_adicionales": campos_display,
        "group_name": get_group_name(request.user),
    }
    return render(request, "incidencias/detalle_incidencia.html", context)
