from django.db import models
from departamentos.models import Departamento

class TipoIncidencia(models.Model):
    nombre = models.CharField(max_length=255)
    descripcion = models.CharField(max_length=255)
    departamento = models.ForeignKey(Departamento, on_delete=models.PROTECT)

    def __str__(self):
        return self.nombre
    
class Encuesta(models.Model):
    ESTADO_CHOICES = [
        ('creado', 'Creado'),
        ('vigente', 'Vigente'),
        ('bloqueado', 'Bloqueado'),
    ]
    titulo = models.CharField(max_length=255)
    descripcion = models.CharField(max_length=400)
    tipo_incidencia = models.ForeignKey(TipoIncidencia, on_delete=models.PROTECT)
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='creado')

    def __str__(self):
        return self.titulo
    
class CamposAdicionales(models.Model):
    titulo = models.CharField(max_length=255)
    encuesta = models.ForeignKey(Encuesta, on_delete=models.CASCADE)
    orden = models.IntegerField() # Como que orden??
    es_obligatoria = models.BooleanField(default=False)

    def __str__(self):
        return self.titulo
