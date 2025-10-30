from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Incidencia, TipoIncidencia
from .forms import TipoIncidenciaForm, IncidenciaForm
from registration.models import Profile
from django.contrib.auth.decorators import login_required

# =======================================================
# VISTAS PARA EL CRUD DE TIPO DE INCIDENCIA
# =======================================================

def listar_tipos_incidencia(request):
    tipos = TipoIncidencia.objects.all()
    return render(request, 'incidencias/listar_tipos_incidencia.html', {'tipos': tipos})

def crear_tipo_incidencia(request):
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
    return render(request, 'incidencias/crear_tipo_incidencia.html', {'form': form, 'titulo_pagina': 'Crear Tipo de Incidencia'})

def editar_tipo_incidencia(request, tipo_id):
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
        form = TipoIncidenciaForm(initial={'nombre': tipo.nombre, 'descripcion': tipo.descripcion, 'departamento': tipo.departamento})
    return render(request, 'incidencias/crear_tipo_incidencia.html', {'form': form, 'titulo_pagina': 'Editar Tipo de Incidencia'})

def eliminar_tipo_incidencia(request, tipo_id):
    tipo = get_object_or_404(TipoIncidencia, id=tipo_id)
    if request.method == 'POST':
        tipo.delete()
        messages.success(request, 'Tipo de incidencia eliminado.')
        return redirect('listar_tipos_incidencia')
    return render(request, 'incidencias/confirmar_eliminar.html', {'objeto': tipo, 'titulo_objeto': 'Tipo de Incidencia'})


# =======================================================
# VISTAS PARA EL CRUD DE INCIDENCIA
# =======================================================

@login_required
def gestion_incidencias(request):
    """Lista de incidencias visible según el perfil del usuario."""
    profile = Profile.objects.get(user=request.user)

    if profile.group.name == "SECPLA":
        incidencias = Incidencia.objects.all()
    elif profile.group.name == "TERRITORIAL":
        incidencias = Incidencia.objects.filter(territorial=request.user)
    elif profile.group.name == "CUADRILLA":
        incidencias = Incidencia.objects.filter(cuadrilla__miembros=request.user)
    else:
        incidencias = Incidencia.objects.none()

    return render(request, 'incidencias/gestion_incidencias.html', {
        'incidencias': incidencias,
        'group_name': profile.group.name
    })

@login_required
def crear_incidencia(request):
    """Crea una incidencia, adaptando el formulario según el grupo del usuario."""
    profile = Profile.objects.get(user=request.user)
    group_name = profile.group.name

    if request.method == 'POST':
        form = IncidenciaForm(request.POST, user=request.user)
        if form.is_valid():
            incidencia = Incidencia(**form.cleaned_data)

            # --- Lógica según perfil ---
            if group_name == "Territorial":
                incidencia.territorial = request.user
                incidencia.estado = 'abierta'  # el territorial siempre crea incidencias abiertas

            incidencia.save()
            messages.success(request, 'Incidencia creada exitosamente.')

            return redirect('gestion_incidencias')

    else:
        form = IncidenciaForm(user=request.user)  # pasa el usuario al form

    return render(request, 'incidencias/formulario_incidencia.html', {
        'form': form,
        'titulo_pagina': 'Crear Incidencia',
        'group_name': group_name
    })


@login_required
def editar_incidencia(request, incidencia_id):
    """Permite editar incidencias según permisos del grupo."""
    profile = Profile.objects.get(user=request.user)
    group_name = profile.group.name

    incidencia = get_object_or_404(Incidencia, id=incidencia_id)

    # Si el usuario es territorial, solo puede editar incidencias suyas
    if group_name == "Territorial" and incidencia.territorial != request.user:
        messages.error(request, "No tienes permisos para editar esta incidencia.")
        return redirect('gestion_incidencias')

    if request.method == 'POST':
        form = IncidenciaForm(request.POST, user=request.user)
        if form.is_valid():
            datos = form.cleaned_data
            for key, value in datos.items():
                setattr(incidencia, key, value)

            # El territorial no puede cambiar estado ni asignar cuadrillas
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
        'group_name': group_name
    })

@login_required
def eliminar_incidencia(request, incidencia_id):
    """Permite eliminar incidencias, restringido según grupo."""
    profile = Profile.objects.get(user=request.user)
    group_name = profile.group.name

    incidencia = get_object_or_404(Incidencia, id=incidencia_id)

    # El territorial solo puede borrar las suyas
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
        'group_name': group_name
    })