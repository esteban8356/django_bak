from django.db import models
from django.contrib.auth.models import User
from apps.elecciones.models import Eleccion

# Create your models here.
class Votante(models.Model):
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='votantes'
    )
    eleccion = models.ForeignKey(
        Eleccion,
        on_delete=models.CASCADE,
        related_name='votantes'
    )
    habilitado = models.BooleanField(default=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['usuario', 'eleccion']

    def __str__(self):
        return f'{self.usuario.username} - {self.eleccion.nombre}'