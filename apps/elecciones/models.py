from django.db import models

# Create your models here.
class Eleccion(models.Model):
    ESTADO_CHOICES = [
        ('borrador', 'Borrador'),
        ('activa', 'Activa'),
        ('cerrada', 'Cerrada'),
    ]

    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    fecha_inicio = models.DateTimeField()
    fecha_cierre = models.DateTimeField()
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='borrador'
    )

    def __str__(self):
        return self.nombre
