from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from registration.models import Profile

@login_required
def main_habilidad(request):
    try:
        profile = Profile.objects.filter(user_id=request.user.id).get()
    except:
         messages.add_message(request, messages.INFO, 'Hubo un error al obtener el perfil.')
         return redirect("login")
    if profile.group_id == 1:
            template_name = 'heroes/main_habilidad.html'
            return render(request, template_name)
    else:
        return redirect("logout")
