from django.shortcuts import render, redirect, get_object_or_404
from .models import Incidencia
from .forms import IncidenciaForm

def gestion_incidencias(request):
    incidencias = Incidencia.objects.select_related(
        'encuesta', 'direccion', 'departamento'
    ).all().order_by('-created_at')
    return render(request, 'incidencias/gestion_incidencias.html', {
        'incidencias': incidencias
    })

def crear_incidencia(request):
    if request.method == 'POST':
        form = IncidenciaForm(request.POST)
        if form.is_valid():
            Incidencia.objects.create(
                encuesta=form.cleaned_data['encuesta'],
                vecino=form.cleaned_data['vecino'],
                territorial=form.cleaned_data['territorial'],
                cuadrilla=form.cleaned_data['cuadrilla'],
                direccion=form.cleaned_data['direccion'],
                departamento=form.cleaned_data['departamento'],
                descripcion=form.cleaned_data['descripcion'],
                latitud=form.cleaned_data['latitud'],
                longitud=form.cleaned_data['longitud'],
                direccion_textual=form.cleaned_data['direccion_textual'],
                estado=form.cleaned_data['estado'],
            )
            return redirect('incidencias:gestion_incidencias')
    else:
        form = IncidenciaForm()

    return render(request, 'incidencias/formulario_incidencia.html', {'form': form})
