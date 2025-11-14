from django.db import models
from django.contrib.auth.models import User
# from departamentos.models import Departamento
from encuestas.models import CamposAdicionales
from cuadrillas.models import Cuadrilla

# class TipoIncidencia(models.Model):
#     nombre = models.CharField(max_length=255)
#     descripcion = models.CharField(max_length=255)
#     departamento = models.ForeignKey(Departamento, on_delete=models.PROTECT)

#     def __str__(self):
#         return self.nombre

class Vecino(models.Model):
    nombre = models.CharField(max_length=255)
    celular = models.CharField(max_length=15)
    email = models.EmailField()
    rut = models.CharField(max_length=12, blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} - {self.rut or self.email}"

class Incidencia(models.Model):
    ESTADO_CHOICES = [
        ('abierta', 'Abierta'),
        ('derivada', 'Derivada'),
        ('proceso', 'Proceso'),
        ('finalizada', 'Finalizada'),
        ('cerrada', 'Cerrada'),
        ('rechazada', 'Rechazada'),
    ]
    encuesta = models.ForeignKey('encuestas.Encuesta', on_delete=models.PROTECT)
    vecino = models.ForeignKey(Vecino, on_delete=models.PROTECT, null=True, blank=True)
    # Ver la opcion de cambiar User a Profile, ya que Profile contiene el grupo del usuario
    territorial = models.ForeignKey(User, on_delete=models.PROTECT, related_name='incidencias_territorial')
    cuadrilla = models.ForeignKey(Cuadrilla, on_delete=models.PROTECT, null=True, blank=True)
    descripcion = models.CharField(max_length=255)
    latitud = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitud = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    direccion_textual = models.CharField(max_length=255, blank=True, null=True)
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='abierta')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Incidencia #{self.id} - {self.descripcion[:20]}"

class Evidencia(models.Model):
    incidencia = models.ForeignKey(Incidencia, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=255)
    # usuario = models.ForeignKey(User, on_delete=models.PROTECT)
    fecha_subida = models.DateTimeField(auto_now_add=True)
    archivo = models.FileField(upload_to='evidencias/')

class EncuestaRespuesta(models.Model):
    incidencia = models.ForeignKey(Incidencia, on_delete=models.CASCADE)
    pregunta = models.ForeignKey(CamposAdicionales, on_delete=models.CASCADE)
    valor = models.TextField()