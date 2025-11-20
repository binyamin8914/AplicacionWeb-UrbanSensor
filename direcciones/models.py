from django.db import models
from django.contrib.auth.models import User

class Direccion(models.Model):
    nombre = models.CharField(max_length=100)
    encargado = models.OneToOneField(User, on_delete=models.PROTECT, related_name='direccion_encargada')
    esta_activa = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre
