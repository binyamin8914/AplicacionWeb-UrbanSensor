from django.urls import path
from .views import SignUpView, ProfileUpdate, EmailUpdate, CustomPasswordResetView
from django.contrib import admin
from registration import views
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy

urlpatterns = [
    path('signup/', SignUpView.as_view(), name="signup"),
    path('profile/', ProfileUpdate.as_view(), name="profile"),  
    path('profile/email/', EmailUpdate.as_view(), name="profile_email"),       
    path('profile_edit/', views.profile_edit, name='profile_edit'),   
    # Inicio del flujo de reset: usa la vista personalizada que genera uid+token y redirige
    path("password_reset/", CustomPasswordResetView.as_view(), name="password_reset"),

    # Rutas para reset de contraseña (confirm y finales) - usadas por Django
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html', success_url=reverse_lazy('password_reset_complete')), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),
]
