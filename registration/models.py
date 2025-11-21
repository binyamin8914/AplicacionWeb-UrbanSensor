from django.contrib.auth.models import Group, User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.shortcuts import get_object_or_404, redirect
from direcciones.models import Direccion


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, default=1) 
    telefono = models.CharField(max_length=30, blank=True)
    token_app_session = models.CharField(max_length = 240,null=True, blank=True, default='')
    first_session = models.CharField(max_length = 240,null=True, blank=True, default='Si')
    direccion = models.ForeignKey(Direccion, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ['user__username']
        permissions = [
            ("can_block_user", "Puede bloquear usuarios"),
        ]
        
    def __str__(self):
        return f"{self.user.username} - {self.group.name}"


