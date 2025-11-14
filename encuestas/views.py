from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction # <-- Importamos transaction
from django.db import IntegrityError # <-- (Ya lo teníamos)

from registration.models import Profile
from .models import Encuesta
# --- Importamos los forms y models necesarios ---
from .forms import EncuestaForm, CamposAdicionalesFormSet
from departamentos.models import Departamento
from incidencias.models import TipoIncidencia


@login_required
def gestion_encuestas(request):
    """
    Lista de encuestas con carga eficiente y paginación.
    (Esta vista está bien como está)
    """
    profile = Profile.objects.get(user=request.user)
    qs = (
        Encuesta.objects
        .select_related('departamento', 'tipo_incidencia')
        .order_by('-id')
    )

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
@transaction.atomic # Protegemos la base de datos
def crear_encuesta(request):
    """
    Crear una encuesta nueva JUNTO con sus campos adicionales.
    (VERSIÓN CORREGIDA con auto-orden)
    """
    profile = Profile.objects.get(user=request.user)

    if request.method == 'POST':
        form = EncuestaForm(request.POST)
        formset = CamposAdicionalesFormSet(request.POST, prefix='campos') 
        
        if form.is_valid():
            # 1. Guardamos el padre en memoria (commit=False)
            encuesta = form.save(commit=False) 
            
            # 2. Conectamos el formset con el padre "borrador"
            formset.instance = encuesta 
            
            # 3. AHORA validamos el formset
            #    (Funciona porque 'orden' ya no es 'required' en el form)
            if formset.is_valid():
                
                # 4. Guardamos el padre en la BD (ahora sí)
                encuesta.save() 
                
                # 5. Obtenemos los formularios "hijos"
                campos = formset.save(commit=False) 
                
                # 6. Iteramos sobre ellos y les damos un número de orden
                orden_count = 1
                for campo in campos:
                    campo.orden = orden_count # Asignamos el número
                    campo.save() # Ahora sí guardamos el campo con su orden
                    orden_count += 1
                
                messages.success(request, '¡La encuesta ha sido creada exitosamente!')
                return redirect('gestion_encuestas')
            else:
                messages.error(request, 'Revisa los campos adicionales, hay errores.')
        else:
             messages.error(request, 'Revisa los campos principales, hay errores.')
    
    else: # Método GET
        form = EncuestaForm()
        formset = CamposAdicionalesFormSet(prefix='campos')

    return render(request, 'encuestas/formulario_encuesta.html', {
        'form': form,
        'formset': formset, 
        'titulo_pagina': 'Crear Nueva Encuesta',
        'modo': 'crear',
        'group_name': profile.group.name,
    })


@login_required
@transaction.atomic 
def editar_encuesta(request, encuesta_id: int):
    """
    Editar encuesta existente Y sus campos adicionales.
    (VERSIÓN CORREGIDA con auto-orden)
    """
    profile = Profile.objects.get(user=request.user)
    encuesta_obj = get_object_or_404(Encuesta, id=encuesta_id)

    if encuesta_obj.estado != 'bloqueado':
        messages.warning(request, 'Solo puedes editar encuestas en estado BLOQUEADO.')
        return redirect('gestion_encuestas')

    if request.method == 'POST':
        form = EncuestaForm(request.POST, instance=encuesta_obj)
        formset = CamposAdicionalesFormSet(request.POST, instance=encuesta_obj, prefix='campos')
        
        if form.is_valid() and formset.is_valid():
            
            # --- ¡NUEVA LÓGICA DE ORDEN!! ---
            form.save() # 1. Guardamos el padre
            
            campos = formset.save(commit=False) # 2. Obtenemos los hijos
            
            orden_count = 1
            for campo in campos:
                campo.orden = orden_count # 3. Asignamos el número
                campo.save() # 4. Guardamos el hijo
                orden_count += 1
            
            # 5. Guardamos los cambios del formset (ej. si se borró uno)
            formset.save_m2m() 
            
            messages.success(request, '¡La encuesta ha sido actualizada exitosamente!')
            return redirect('gestion_encuestas')
        else:
            messages.error(request, 'Revisa los campos: hay errores en el formulario.')
    
    else: # Método GET
        form = EncuestaForm(instance=encuesta_obj)
        formset = CamposAdicionalesFormSet(instance=encuesta_obj, prefix='campos') 

    return render(request, 'encuestas/formulario_encuesta.html', {
        'form': form,
        'formset': formset, 
        'titulo_pagina': 'Editar Encuesta',
        'modo': 'editar',
        'encuesta': encuesta_obj,
        'group_name': profile.group.name,
    })


@login_required
def eliminar_encuesta(request, encuesta_id: int):
    """
    Confirmar y eliminar una encuesta.
    (Esta vista está bien como está)
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