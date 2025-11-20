from django.urls import path
from .views import SignUpView, ProfileUpdate, EmailUpdate
from django.contrib import admin
from registration import views
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy

urlpatterns = [
    path('signup/', SignUpView.as_view(), name="signup"),
    path('profile/', ProfileUpdate.as_view(), name="profile"),  
    path('profile/email/', EmailUpdate.as_view(), name="profile_email"),       
    path('profile_edit/', views.profile_edit, name='profile_edit'),   

    path("reset_password_form/", views.reset_password_form, name="reset_password_form"),
    path("reset_password_change/", views.reset_password_change, name="reset_password_change"),
    path("reset_password_change/<str:email>/", views.reset_password_change, name="reset_password_change"),
    ]
