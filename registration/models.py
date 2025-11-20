from django.contrib.auth.models import Group, User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.shortcuts import get_object_or_404, redirect

# Equivalencias entre el codigo y el modelo
#  - ------------------------------------------------------------------------
#  - | Nombre de la tabla en el modelo  | Nombre de la tabla en el codigo   |
#  - ------------------------------------------------------------------------
#  - | Usuario                          | Profile                           |
#  - | -------                          | User                              | -> Tabla manejada por django, contiene la mitad de los datos de la tabla Usuarios del modelo
#  - | Perfiles                         | Group                             | -> Group es una tabla manejada por django
#  - ------------------------------------------------------------------------

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, default=1) 
    telefono = models.CharField(max_length=30, blank=True)
    token_app_session = models.CharField(max_length = 240,null=True, blank=True, default='')
    first_session = models.CharField(max_length = 240,null=True, blank=True, default='Si')

    class Meta:
        ordering = ['user__username']
        permissions = [
            ("can_block_user", "Puede bloquear usuarios"),
        ]
        
    def __str__(self):
        return f"{self.user.username} - {self.group.name}"


