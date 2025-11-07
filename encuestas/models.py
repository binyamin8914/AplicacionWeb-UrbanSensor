from django.db import models
from departamentos.models import Departamento

class Vecino(models.Model):
    nombre = models.CharField(max_length=255)
    celular = models.CharField(max_length=15)
    email = models.EmailField()
    rut = models.CharField(max_length=12, blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} - {self.rut or self.email}"
    
class Encuesta(models.Model):
    ESTADO_CHOICES = [
        ('creado', 'Creado'),
        ('vigente', 'Vigente'),
        ('bloqueado', 'Bloqueado'),
    ]
    PRIORIDAD_CHOICES = [
        ('alta', 'Alta'),
        ('normal', 'Normal'),
        ('baja', 'Baja'),
    ]
    titulo = models.CharField(max_length=255)
    descripcion = models.CharField(max_length=400)
    tipo_incidencia = models.ForeignKey('incidencias.TipoIncidencia', on_delete=models.PROTECT)
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='creado')
    prioridad = models.CharField(max_length=10, choices=PRIORIDAD_CHOICES, default='normal')
    departamento = models.ForeignKey(Departamento, on_delete=models.PROTECT)

    def __str__(self):
        return self.titulo
    
class CamposAdicionales(models.Model):
    titulo = models.CharField(max_length=255)
    encuesta = models.ForeignKey(Encuesta, on_delete=models.CASCADE)
    orden = models.IntegerField()
    es_obligatoria = models.BooleanField(default=False)

    def __str__(self):
        return self.titulo
    
class EncuestaRespuesta(models.Model):
    incidencia = models.ForeignKey('incidencias.Incidencia', on_delete=models.CASCADE)
    pregunta = models.ForeignKey(CamposAdicionales, on_delete=models.CASCADE)
    valor = models.TextField()
