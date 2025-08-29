from django.db import models
from administracion.models import Direccion, Departamento, Cuadrilla
from django.contrib.auth.models import User

class TipoIncidencia(models.Model):
    nombre = models.CharField(max_length=255)
    descripcion = models.CharField(max_length=255)
    departamento = models.ForeignKey(Departamento, on_delete=models.PROTECT)

    def __str__(self):
        return self.nombre

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
    tipo_incidencia = models.ForeignKey(TipoIncidencia, on_delete=models.PROTECT)
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

class Incidencia(models.Model):
    ESTADO_CHOICES = [
        ('abierta', 'Abierta'),
        ('derivada', 'Derivada'),
        ('proceso', 'Proceso'),
        ('finalizada', 'Finalizada'),
        ('cerrada', 'Cerrada'),
        ('rechazada', 'Rechazada'),
    ]
    encuesta = models.ForeignKey(Encuesta, on_delete=models.PROTECT)
    vecino = models.ForeignKey(Vecino, on_delete=models.PROTECT, null=True, blank=True) 
    territorial = models.ForeignKey(User, on_delete=models.PROTECT, related_name='incidencias_territorial')
    cuadrilla = models.ForeignKey(Cuadrilla, on_delete=models.PROTECT)
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
    tipo = models.CharField(max_length=255)
    descripcion = models.CharField(max_length=255)
    usuario = models.ForeignKey(User, on_delete=models.PROTECT)
    fecha_subida = models.DateTimeField(auto_now_add=True)
    archivo = models.FileField(upload_to='evidencias/')

class EncuestaRespuesta(models.Model):
    incidencia = models.ForeignKey(Incidencia, on_delete=models.CASCADE)
    pregunta = models.ForeignKey(CamposAdicionales, on_delete=models.CASCADE)
    valor = models.TextField()
