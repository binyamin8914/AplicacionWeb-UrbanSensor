from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from registration.models import Profile
from heroes.models import Habilidad

@login_required
def main_habilidad(request):
    try:
        profile = Profile.objects.filter(user_id=request.user.id).get()
    except:
         messages.add_message(request, messages.INFO, 'Hubo un error al obtener el perfil.')
         return redirect("login")
    if profile.group_id == 1:
            habilidad_listado = Habilidad.objects.filter(state="Activo").order_by('habilidad')
            template_name = 'heroes/main_habilidad.html'
            return render(request, template_name, {'habilidad_listado': habilidad_listado})
    else:
        return redirect("logout")
    
@login_required
def habilidad_crear(request):
    try:
        profile = Profile.objects.filter(user_id=request.user.id).get()
    except:
         messages.add_message(request, messages.INFO, 'Hubo un error al obtener el perfil.')
         return redirect("login")
    if profile.group_id == 1:
            template_name = 'heroes/habilidad_crear.html'
            return render(request, template_name)
    else:
        return redirect("logout")
    

@login_required    
def habilidad_guardar(request):
        try:
            profile = Profile.objects.filter(user_id=request.user.id).get()
        except:
            messages.add_message(request, messages.INFO, 'Hubo un error al obtener el perfil.')
            return redirect("login")
        if profile.group_id == 1:
            if request.method == 'POST':
                habilidad = request.POST.get('habilidad')
                descripcion = request.POST.get('descripcion')
                if habilidad == '' or descripcion == '':
                    messages.add_message(request, messages.INFO, 'Debes ingresar toda la información.')
                    return redirect("habilidad_crear")
                habilidad_save = Habilidad(
                    habilidad=habilidad,
                    descripcion=descripcion
                    )
                habilidad_save.save()
                messages.add_message(request, messages.INFO, 'Habilidad creada correctamente.')
                return redirect("main_habilidad")
            else:
                messages.add_message(request, messages.INFO, 'Hubo un error al procesar el formulario.')
                return redirect("main_habilidad")
        else:
            return redirect("logout")
