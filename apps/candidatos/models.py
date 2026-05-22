'''from django.db import models

# Create your models here.
class candidato(models.Model):
    name = models.TextField("Nombre")

    def __str__(self):
        return f'{self.name}'''
from django.db import models
from apps.elecciones.models import Eleccion

class Candidato(models.Model):
    eleccion = models.ForeignKey(
        Eleccion,
        on_delete=models.CASCADE,
        related_name='candidatos'
    )
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    propuesta = models.TextField(blank=True)

    def __str__(self):
        return f'{self.nombre} - {self.eleccion.nombre}'