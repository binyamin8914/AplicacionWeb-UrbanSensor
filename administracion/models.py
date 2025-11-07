<<<<<<< HEAD
from django.db import models
=======
from django.db import models
from django.contrib.auth.models import User

class Direccion(models.Model):
    nombre = models.CharField(max_length=100)
    encargado = models.OneToOneField(User, on_delete=models.PROTECT, related_name='direccion_encargada')
    correo_encargado = models.EmailField()
    esta_activa = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

class Departamento(models.Model):
    nombre = models.CharField(max_length=255)
    encargado = models.OneToOneField(User, on_delete=models.PROTECT, related_name='departamento_encargado')
    correo_encargado = models.EmailField()
    direccion = models.ForeignKey(Direccion, on_delete=models.PROTECT)
    esta_activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

class Cuadrilla(models.Model):
    nombre = models.CharField(max_length=255)
    encargado = models.OneToOneField(User, on_delete=models.PROTECT, related_name='cuadrilla_encargada')
    departamento = models.ForeignKey(Departamento, on_delete=models.PROTECT)
    esta_activa = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre
>>>>>>> dd07e64c90885b997006adea9d8508f590459c99
