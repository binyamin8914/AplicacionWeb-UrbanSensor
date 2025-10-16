from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Incidencia, TipoIncidencia
from .forms import TipoIncidenciaForm, IncidenciaForm

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
    return render(request, 'incidencias/formulario_generico.html', {'form': form, 'titulo_pagina': 'Crear Tipo de Incidencia'})

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
    return render(request, 'incidencias/formulario_generico.html', {'form': form, 'titulo_pagina': 'Editar Tipo de Incidencia'})

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

def gestion_incidencias(request):
    incidencias = Incidencia.objects.all()
    return render(request, 'incidencias/gestion_incidencias.html', {'incidencias': incidencias})

def crear_incidencia(request):
    if request.method == 'POST':
        form = IncidenciaForm(request.POST)
        if form.is_valid():
            Incidencia.objects.create(**form.cleaned_data)
            messages.success(request, 'Incidencia creada exitosamente.')
            return redirect('gestion_incidencias')
    else:
        form = IncidenciaForm()
    return render(request, 'incidencias/formulario_incidencia.html', {'form': form, 'titulo_pagina': 'Crear Incidencia'})

def editar_incidencia(request, incidencia_id):
    incidencia = get_object_or_404(Incidencia, id=incidencia_id)
    if request.method == 'POST':
        form = IncidenciaForm(request.POST)
        if form.is_valid():
            datos = form.cleaned_data
            for key, value in datos.items():
                setattr(incidencia, key, value)
            incidencia.save()
            messages.success(request, 'Incidencia actualizada.')
            return redirect('gestion_incidencias')
    else:
        # Creamos un diccionario con los datos iniciales para el formulario
        datos_iniciales = {
            'encuesta': incidencia.encuesta, 'vecino': incidencia.vecino,
            'territorial': incidencia.territorial, 'cuadrilla': incidencia.cuadrilla,
            'descripcion': incidencia.descripcion, 'latitud': incidencia.latitud,
            'longitud': incidencia.longitud, 'direccion_textual': incidencia.direccion_textual,
            'estado': incidencia.estado,
        }
        form = IncidenciaForm(initial=datos_iniciales)
    return render(request, 'incidencias/formulario_incidencia.html', {'form': form, 'titulo_pagina': 'Editar Incidencia'})

def eliminar_incidencia(request, incidencia_id):
    incidencia = get_object_or_404(Incidencia, id=incidencia_id)
    if request.method == 'POST':
        incidencia.delete()
        messages.success(request, 'Incidencia eliminada.')
        return redirect('gestion_incidencias')
    return render(request, 'incidencias/confirmar_eliminar.html', {'objeto': incidencia, 'titulo_objeto': 'Incidencia'})