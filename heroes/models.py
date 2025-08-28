from django.db import models

class Habilidad(models.Model):
    habilidad = models.CharField(max_length=240,null=True, blank=True)
    descripcion = models.CharField(max_length=240,null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True, default='Activo')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Habilidad'
        verbose_name_plural = 'Habilidades'
        ordering = ['habilidad']

    def __str__(self):
        return self.habilidad

class Heroe(models.Model):
    habilidad = models.ForeignKey(Habilidad, on_delete=models.CASCADE)
    nombre_heroe = models.CharField(max_length=100,null=True, blank=True)
    nivel = models.IntegerField(null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True, default='Activo')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Heroe'
        verbose_name_plural = 'Heroes'
        ordering = ['nombre_heroe']

    def __str__(self):
        return self.nombre_heroe