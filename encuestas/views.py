from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from registration.models import Profile
from .models import Encuesta
from .forms import EncuestaForm


@login_required
def gestion_encuestas(request):
    """
    Lista de encuestas con carga eficiente y paginación.
    Admite filtros opcionales por estado/prioridad vía querystring (?estado= / ?prioridad=).
    """
    profile = Profile.objects.get(user=request.user)

    qs = (
        Encuesta.objects
        .select_related('departamento', 'tipo_incidencia')
        .order_by('-id')
    )

    # Filtros opcionales
    estado = request.GET.get('estado')
    prioridad = request.GET.get('prioridad')
    if estado:
        qs = qs.filter(estado=estado)
    if prioridad:
        qs = qs.filter(prioridad=prioridad)

    page_obj = Paginator(qs, 10).get_page(request.GET.get('page'))
    return render(request, 'encuestas/gestion_encuestas.html', {
        'encuestas': page_obj,
        'f_estado': estado or '',
        'f_prioridad': prioridad or '',
        'group_name': profile.group.name,
    })


@login_required
def crear_encuesta(request):
    """
    Crear una encuesta nueva.
    """
    profile = Profile.objects.get(user=request.user)

    if request.method == 'POST':
        form = EncuestaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '¡La encuesta ha sido creada exitosamente!')
            return redirect('gestion_encuestas')
        messages.error(request, 'Revisa los campos: hay errores en el formulario.')
    else:
        form = EncuestaForm()

    return render(request, 'encuestas/formulario_encuesta.html', {
        'form': form,
        'titulo_pagina': 'Crear Nueva Encuesta',
        'modo': 'crear',
        'group_name': profile.group.name,
    })


@login_required
def editar_encuesta(request, encuesta_id: int):
    """
    Editar encuesta existente.
    Requisito: solo se puede editar si la encuesta está en estado BLOQUEADO.
    """
    profile = Profile.objects.get(user=request.user)
    encuesta_obj = get_object_or_404(Encuesta, id=encuesta_id)

    if encuesta_obj.estado != 'bloqueado':
        messages.warning(request, 'Solo puedes editar encuestas en estado BLOQUEADO.')
        return redirect('gestion_encuestas')

    if request.method == 'POST':
        form = EncuestaForm(request.POST, instance=encuesta_obj)
        if form.is_valid():
            form.save()
            messages.success(request, '¡La encuesta ha sido actualizada exitosamente!')
            return redirect('gestion_encuestas')
        messages.error(request, 'Revisa los campos: hay errores en el formulario.')
    else:
        form = EncuestaForm(instance=encuesta_obj)

    return render(request, 'encuestas/formulario_encuesta.html', {
        'form': form,
        'titulo_pagina': 'Editar Encuesta',
        'modo': 'editar',
        'encuesta': encuesta_obj,
        'group_name': profile.group.name,
    })


@login_required
def eliminar_encuesta(request, encuesta_id: int):
    """
    Confirmar y eliminar una encuesta.
    """
    profile = Profile.objects.get(user=request.user)
    encuesta_obj = get_object_or_404(Encuesta, id=encuesta_id)

    if request.method == 'POST':
        encuesta_obj.delete()
        messages.success(request, '¡La encuesta ha sido eliminada!')
        return redirect('gestion_encuestas')

    return render(request, 'encuestas/confirmar_eliminar_encuesta.html', {
        'encuesta': encuesta_obj,
        'group_name': profile.group.name,
    })
