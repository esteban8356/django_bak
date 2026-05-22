from django.db import models
from django.contrib.auth.models import User
from apps.elecciones.models import Eleccion
from apps.candidatos.models import Candidato

# Create your models here.
class Voto(models.Model):
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='votos'
    )
    eleccion = models.ForeignKey(
        Eleccion,
        on_delete=models.CASCADE,
        related_name='votos'
    )
    candidato = models.ForeignKey(
        Candidato,
        on_delete=models.CASCADE,
        related_name='votos'
    )
    fecha_voto = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['usuario', 'eleccion']

    def __str__(self):
        return f'{self.usuario.username} votó en {self.eleccion.nombre}'