from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Incidencia
from .forms import IncidenciaForm

def gestion_incidencias(request):
    incidencias = Incidencia.objects.all().order_by('-created_at')
    return render(request, 'incidencias/gestion_incidencias.html', {'incidencias': incidencias})

def crear_incidencia(request):
    if request.method == 'POST':
        form = IncidenciaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Incidencia creada correctamente.")
            return redirect('incidencias:gestion_incidencias')
    else:
        form = IncidenciaForm()
    return render(request, 'incidencias/formulario_incidencia.html', {'form': form})

def editar_incidencia(request, incidencia_id):
    incidencia = get_object_or_404(Incidencia, id=incidencia_id)
    if request.method == 'POST':
        form = IncidenciaForm(request.POST, instance=incidencia)
        if form.is_valid():
            form.save()
            messages.success(request, "Incidencia actualizada correctamente.")
            return redirect('incidencias:gestion_incidencias')
    else:
        form = IncidenciaForm(instance=incidencia)
    return render(request, 'incidencias/formulario_incidencia.html', {'form': form})

def eliminar_incidencia(request, incidencia_id):
    incidencia = get_object_or_404(Incidencia, id=incidencia_id)
    if request.method == 'POST':
        incidencia.delete()
        messages.success(request, "Incidencia eliminada correctamente.")
        return redirect('incidencias:gestion_incidencias')
    return render(request, 'incidencias/confirmar_eliminar_incidencia.html', {'incidencia': incidencia})
