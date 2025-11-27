from .forms import UserCreationFormWithEmail, EmailForm
from django.views.generic import CreateView
from django.views.generic.edit import UpdateView
from django.contrib.auth.views import PasswordResetView
from django.contrib.auth.models import User, Group
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy, reverse
from django.shortcuts import render, redirect
from django import forms
from .models import Profile


from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

class SignUpView(CreateView):
    form_class = UserCreationFormWithEmail
    template_name = 'registration/signup.html'

    def get_success_url(self):
        return reverse_lazy('login') + '?register'
    
    def get_form(self, form_class=None):
        form = super(SignUpView,self).get_form()
   
        form.fields['username'].widget = forms.TextInput(attrs={'class':'form-control mb-2','placeholder':'Nombre de usuario'})
        form.fields['email'].widget = forms.EmailInput(attrs={'class':'form-control mb-2','placeholder':'Dirección de correo'})
        form.fields['password1'].widget = forms.PasswordInput(attrs={'class':'form-control mb-2','placeholder':'Ingrese su contraseña'})
        form.fields['password2'].widget = forms.PasswordInput(attrs={'class':'form-control mb-2','placeholder':'Re ingrese su contraseña'})    
        return form

@method_decorator(login_required, name='dispatch')
class ProfileUpdate(UpdateView):

    success_url = reverse_lazy('profile')
    template_name = 'registration/profiles_form.html'

    def get_object(self):
        
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        return profile

@method_decorator(login_required, name='dispatch')
class EmailUpdate(UpdateView):
    form_class = EmailForm
    success_url = reverse_lazy('check_group_main')
    template_name = 'registration/profile_email_form.html'

    def get_object(self):
        
        return self.request.user
    
    def get_form(self, form_class=None):
        form = super(EmailUpdate,self).get_form()
        
        form.fields['email'].widget = forms.EmailInput(attrs={'class':'form-control mb-2','placeholder':'Dirección de correo'})
        return form
@login_required
def profile_edit(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        mobile = request.POST.get('mobile')
        phone = request.POST.get('phone')
        User.objects.filter(pk=request.user.id).update(first_name=first_name)
        User.objects.filter(pk=request.user.id).update(last_name=last_name)
        Profile.objects.filter(user_id=request.user.id).update(phone=phone)
        Profile.objects.filter(user_id=request.user.id).update(mobile=mobile)
        messages.add_message(request, messages.INFO, 'Perfil Editado con éxito') 
    profile = Profile.objects.get(user_id = request.user.id)
    template_name = 'registration/profile_edit.html'
    return render(request,template_name,{'profile':profile})

def reset_password_form(request):
    template_name = "registration/reset_password_form.html"
    if request.method == "POST":
        email = request.POST.get("email")
        user_with_email = User.objects.filter(email=email)
        if user_with_email.count() > 1:
            return render(request, template_name, {"mensaje": "Existen varios usuarios con ese correo. Contacta con un administrador"})
        elif user_with_email.count() == 0:
            return render(request, template_name, {"mensaje": "No existen usuarios con ese correo"})
        url = reverse("reset_password_change")
        return redirect(f"{url}?email={email}")
    return render(request, template_name)

def reset_password_change(request):
    template_name = "registration/reset_password_change.html"
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("new_password1")
        password2 = request.POST.get("new_password2")
        if password != password2:
            return render(request, template_name, {"email": request.GET.get("email"), "mensaje": "Las contraseñas no coinciden"})
        user = User.objects.get(email=email)
        user.set_password(password)
        user.save()
        return redirect("login")
    return render(request, template_name, {"email": request.GET.get("email")})

