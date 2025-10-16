from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Encuesta, CamposAdicionales, EncuestaRespuesta
from .forms import EncuestaForm # ¡Importante! El siguiente paso será crear este archivo

# Vista principal para mostrar todas las encuestas
def gestion_encuestas(request):
    """
    Muestra una lista de todas las encuestas. Es la página principal de gestión.
    """
    lista_encuestas = Encuesta.objects.all()
    contexto = {
        'encuestas': lista_encuestas
    }
    return render(request, 'encuestas/gestion_encuestas.html', contexto)

# Vista para crear una nueva encuesta
def crear_encuesta(request):
    """
    Maneja la creación de una nueva encuesta a través de un formulario.
    """
    if request.method == 'POST':
        form = EncuestaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '¡La encuesta ha sido creada exitosamente!')
            return redirect('gestion_encuestas') # Redirige a la lista después de crear
    else:
        form = EncuestaForm() # Si es GET, crea un formulario vacío

    contexto = {
        'form': form,
        'titulo_pagina': 'Crear Nueva Encuesta'
    }
    return render(request, 'encuestas/formulario_encuesta.html', contexto)

# Vista para editar una encuesta existente
def editar_encuesta(request, encuesta_id):
    """
    Busca una encuesta por su ID y maneja su edición.
    """
    encuesta_obj = get_object_or_404(Encuesta, id=encuesta_id) # Busca la encuesta o devuelve un error 404
    if request.method == 'POST':
        form = EncuestaForm(request.POST, instance=encuesta_obj)
        if form.is_valid():
            form.save()
            messages.success(request, '¡La encuesta ha sido actualizada exitosamente!')
            return redirect('gestion_encuestas')
    else:
        form = EncuestaForm(instance=encuesta_obj) # Rellena el formulario con los datos existentes

    contexto = {
        'form': form,
        'titulo_pagina': 'Editar Encuesta'
    }
    return render(request, 'encuestas/formulario_encuesta.html', contexto)

# Vista para eliminar una encuesta
def eliminar_encuesta(request, encuesta_id):
    """
    Busca una encuesta por su ID y la elimina después de una confirmación.
    """
    encuesta_obj = get_object_or_404(Encuesta, id=encuesta_id)
    if request.method == 'POST':
        encuesta_obj.delete()
        messages.success(request, '¡La encuesta ha sido eliminada!')
        return redirect('gestion_encuestas')

    contexto = {
        'encuesta': encuesta_obj
    }
    return render(request, 'encuestas/confirmar_eliminar_encuesta.html', contexto)