from django.db import models
from django.contrib.auth.models import User
from direcciones.models import Direccion

class Departamento(models.Model):
    nombre = models.CharField(max_length=255)
    encargado = models.OneToOneField(User, on_delete=models.PROTECT, related_name='departamento_encargado')
    direccion = models.ForeignKey(Direccion, on_delete=models.PROTECT)
    esta_activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre
