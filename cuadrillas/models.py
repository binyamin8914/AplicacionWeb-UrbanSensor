from django.db import models
from django.contrib.auth.models import User
from departamentos.models import Departamento

class Cuadrilla(models.Model):
    nombre = models.CharField(max_length=255)
    encargado = models.OneToOneField(User, on_delete=models.PROTECT, related_name='cuadrilla_encargada')
    departamento = models.ForeignKey(Departamento, on_delete=models.PROTECT)
    esta_activa = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre