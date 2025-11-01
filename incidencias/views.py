from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Incidencia, TipoIncidencia
from .forms import TipoIncidenciaForm, IncidenciaForm
from registration.models import Profile
from django.contrib.auth.decorators import login_required

# =======================================================
# CRUD TIPO DE INCIDENCIA
# =======================================================

@login_required
def listar_tipos_incidencia(request):
    profile = Profile.objects.get(user=request.user)
    group_name = profile.group.name

    tipos = TipoIncidencia.objects.all()

    return render(request, 'incidencias/listar_tipos_incidencia.html', {
        'tipos': tipos,
        'group_name': group_name,
    })


@login_required
def crear_tipo_incidencia(request):
    profile = Profile.objects.get(user=request.user)
    group_name = profile.group.name

    if request.method == 'POST':
        form = TipoIncidenciaForm(request.POST)
        if form.is_valid():
            datos = form.cleaned_data
            TipoIncidencia.objects.create(
                nombre=datos['nombre'],
                descripcion=datos['descripcion'],
                departamento=datos['departamento']
            )
            messages.success(request, 'Tipo de incidencia creado exitosamente.')
            return redirect('listar_tipos_incidencia')
    else:
        form = TipoIncidenciaForm()

    return render(request, 'incidencias/crear_tipo_incidencia.html', {
        'form': form,
        'titulo_pagina': 'Crear Tipo de Incidencia',
        'group_name': group_name,
    })


@login_required
def editar_tipo_incidencia(request, tipo_id):
    profile = Profile.objects.get(user=request.user)
    group_name = profile.group.name

    tipo = get_object_or_404(TipoIncidencia, id=tipo_id)

    if request.method == 'POST':
        form = TipoIncidenciaForm(request.POST)
        if form.is_valid():
            datos = form.cleaned_data
            tipo.nombre = datos['nombre']
            tipo.descripcion = datos['descripcion']
            tipo.departamento = datos['departamento']
            tipo.save()
            messages.success(request, 'Tipo de incidencia actualizado.')
            return redirect('listar_tipos_incidencia')

    else:
        form = TipoIncidenciaForm(initial={
            'nombre': tipo.nombre,
            'descripcion': tipo.descripcion,
            'departamento': tipo.departamento
        })

    return render(request, 'incidencias/crear_tipo_incidencia.html', {
        'form': form,
        'titulo_pagina': 'Editar Tipo de Incidencia',
        'group_name': group_name,
    })


@login_required
def eliminar_tipo_incidencia(request, tipo_id):
    profile = Profile.objects.get(user=request.user)
    group_name = profile.group.name

    tipo = get_object_or_404(TipoIncidencia, id=tipo_id)

    if request.method == 'POST':
        tipo.delete()
        messages.success(request, 'Tipo de incidencia eliminado.')
        return redirect('listar_tipos_incidencia')

    return render(request, 'incidencias/confirmar_eliminar.html', {
        'objeto': tipo,
        'titulo_objeto': 'Tipo de Incidencia',
        'group_name': group_name
    })


# =======================================================
# CRUD INCIDENCIAS
# =======================================================

@login_required
def gestion_incidencias(request):
    profile = Profile.objects.get(user=request.user)
    group_name = profile.group.name

    if group_name == "SECPLA":
        incidencias = Incidencia.objects.all()
    elif group_name == "TERRITORIAL":
        incidencias = Incidencia.objects.filter(territorial=request.user)
    elif group_name == "CUADRILLA":
        incidencias = Incidencia.objects.filter(cuadrilla__miembros=request.user)
    else:
        incidencias = Incidencia.objects.none()

    return render(request, 'incidencias/gestion_incidencias.html', {
        'incidencias': incidencias,
        'group_name': group_name,
    })


@login_required
def crear_incidencia(request):
    profile = Profile.objects.get(user=request.user)
    group_name = profile.group.name

    if request.method == 'POST':
        form = IncidenciaForm(request.POST)

        if form.is_valid():
            datos = form.cleaned_data

            Incidencia.objects.create(
                encuesta=datos['encuesta'],
                vecino=datos['vecino'],
                territorial=datos['territorial'],
                cuadrilla=datos['cuadrilla'],
                descripcion=datos['descripcion'],
                latitud=datos['latitud'],
                longitud=datos['longitud'],
                direccion_textual=datos['direccion_textual'],
                estado=datos['estado'],
            )

            messages.success(request, "Incidencia creada correctamente.")
            return redirect('gestion_incidencias')

        else:
            messages.error(request, "Hay errores en el formulario.")

    else:
        form = IncidenciaForm()

    return render(request, 'incidencias/formulario_incidencia.html', {
        'form': form,
        'titulo_pagina': 'Crear Incidencia',
        'group_name': group_name,
    })


@login_required
def editar_incidencia(request, incidencia_id):
    profile = Profile.objects.get(user=request.user)
    group_name = profile.group.name

    incidencia = get_object_or_404(Incidencia, id=incidencia_id)

    if group_name == "Territorial" and incidencia.territorial != request.user:
        messages.error(request, "No tienes permisos para editar esta incidencia.")
        return redirect('gestion_incidencias')

    if request.method == 'POST':
        form = IncidenciaForm(request.POST, user=request.user)
        if form.is_valid():
            datos = form.cleaned_data
            for key, value in datos.items():
                setattr(incidencia, key, value)

            if group_name == "Territorial":
                incidencia.territorial = request.user

            incidencia.save()
            messages.success(request, 'Incidencia actualizada.')
            return redirect('gestion_incidencias')

    else:
        datos_iniciales = {
            'encuesta': incidencia.encuesta,
            'vecino': incidencia.vecino,
            'territorial': incidencia.territorial,
            'cuadrilla': incidencia.cuadrilla,
            'descripcion': incidencia.descripcion,
            'latitud': incidencia.latitud,
            'longitud': incidencia.longitud,
            'direccion_textual': incidencia.direccion_textual,
            'estado': incidencia.estado,
        }
        form = IncidenciaForm(initial=datos_iniciales, user=request.user)

    return render(request, 'incidencias/formulario_incidencia.html', {
        'form': form,
        'titulo_pagina': 'Editar Incidencia',
        'group_name': group_name,
    })


@login_required
def eliminar_incidencia(request, incidencia_id):
    profile = Profile.objects.get(user=request.user)
    group_name = profile.group.name

    incidencia = get_object_or_404(Incidencia, id=incidencia_id)

    if group_name == "Territorial" and incidencia.territorial != request.user:
        messages.error(request, "No puedes eliminar una incidencia que no creaste.")
        return redirect('gestion_incidencias')

    if request.method == 'POST':
        incidencia.delete()
        messages.success(request, 'Incidencia eliminada.')
        return redirect('gestion_incidencias')

    return render(request, 'incidencias/confirmar_eliminar.html', {
        'objeto': incidencia,
        'titulo_objeto': 'Incidencia',
        'group_name': group_name,
    })
