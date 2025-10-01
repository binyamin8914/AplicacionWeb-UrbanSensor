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

@login_required
def habilidad_ver(request, habilidad_id):
    try:
        profile = Profile.objects.filter(user_id=request.user.id).get()
    except:
         messages.add_message(request, messages.INFO, 'Hubo un error al obtener el perfil.')
         return redirect("logout")
    if profile.group_id == 1:
            try:
                habilidad_count = Habilidad.objects.filter(pk=habilidad_id).count()
                if habilidad_count <= 0:
                    messages.add_message(request, messages.INFO, 'No se encontró la habilidad.')
                    return redirect('check_profile')
                habilidad_data = Habilidad.objects.get(pk=habilidad_id)
            except:
                messages.add_message(request, messages.INFO, 'Hubo un error.')
                return redirect("check_profile")
            template_name = 'heroes/habilidad_ver.html'
            return render(request, template_name, {'habilidad_data': habilidad_data})
    else:
        return redirect("logout")
    

@login_required
def habilidad_actualiza(request, habilidad_id=None):
    try:
        profile = Profile.objects.filter(user_id=request.user.id).get()
    except:
         messages.add_message(request, messages.INFO, "Hubo un error al obtener el perfil.")
         return redirect("logout")
    if profile.group_id == 1:
         try:
              if request.method == 'POST':
                   id_habilidad = request.POST.get('id_habilidad')
                   habilidad = request.POST.get('habilidad')
                   descripcion = request.POST.get('descripcion')
                   habilidad_count = Habilidad.objects.filter(pk=id_habilidad).count()
                   if habilidad_count <= 0:
                        messages.add_message(request, messages.INFO, 'No se encontró la habilidad.')
                        return redirect('logout')
                   if habilidad == '' or descripcion == '':
                        messages.add_message(request, messages.INFO, 'Hubo un error')
                        return redirect('main_habilidad')
                   Habilidad.objects.filter(pk=id_habilidad).update(habilidad=habilidad)
                   Habilidad.objects.filter(pk=id_habilidad).update(descripcion=descripcion)
                   messages.add_message(request, messages.INFO, 'Habilidad actualizada')
                   return redirect('main_habilidad')
         except:
              messages.add_message(request, messages.INFO, 'Hubo un error')
              return redirect('check_profile')
         '''
         se comprueba si habilidad_id que se pasa como argumento existe como dato
         en caso de no existir retorna un error, de existir, se instancia un objeto
         '''
         try:
              habilidad_count = Habilidad.objects.filter(pk=habilidad_id).count()
              if habilidad_count <= 0:
                   messages.add_message(request, messages.INFO, 'No se encontró la habilidad.')
                   return redirect('check_profile')
              habilidad_data = Habilidad.objects.get(pk=habilidad_id) #genera un objeto no iterable
         except:
              messages.add_message(request, messages.INFO, 'Hubo un error')
              return redirect('logout')
         template_name = 'heroes/habilidad_actualiza.html'
         return render(request,template_name,{'habilidad_data':habilidad_data})
    else:
         return redirect('logout')
    

@login_required
def habilidad_bloquea(request, habilidad_id):
     try:
          profile= Profile.objects.filter(user_id=request.user.id).get()
     except:
          messages.add_message(request, messages.INFO, "Hubo un error al obtener el perfil.")
          return redirect("logout")
     if profile.group_id == 1:
          habilidad_count = Habilidad.objects.filter(pk=habilidad_id).count()
          if habilidad_count <= 0:
               messages.add_message(request, messages.INFO, 'No se encontró la habilidad.')
               return redirect('check_profile')
          Habilidad.objects.filter(pk=habilidad_id).update(state='Bloqueado')
          messages.add_message(request, messages.INFO, 'Habilidad bloqueada.')
          return redirect('main_habilidad')
     else:
          messages.add_message(request, messages.INFO, 'Hubo un error.')
          return redirect('logout')
     
@login_required
def habilidad_elimina(request, habilidad_id):
     try:
          profile = Profile.objects.filter(user_id=request.user.id).get()
     except:
            messages.add_message(request, messages.INFO, "Hubo un error al obtener el perfil.")
            return redirect("logout")
     if profile.group_id == 1:
          habilidad_count = Habilidad.objects.filter(pk=habilidad_id).count()
          if habilidad_count <= 0:
               messages.add_message(request, messages.INFO, 'Hubo un error')
               return redirect('check_profile')
          Habilidad.objects.filter(pk=habilidad_id).delete()
          messages.add_message(request, messages.INFO, 'Habilidad eliminada.')
          return redirect('main_habilidad')
     else:
            messages.add_message(request, messages.INFO, 'Hubo un error.')
            return redirect('logout')

     
