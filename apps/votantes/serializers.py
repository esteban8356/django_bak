from rest_framework import serializers
from .models import Votante

class VotanteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Votante
        fields = '__all__'

    def validate(self, data):
        usuario = data.get('usuario')
        eleccion = data.get('eleccion')

        # Verificar que la elección no esté cerrada
        if eleccion and eleccion.estado == 'cerrada':
            raise serializers.ValidationError(
                "No se pueden habilitar votantes en una elección cerrada."
            )

        # Verificar que no esté ya registrado
        if Votante.objects.filter(usuario=usuario, eleccion=eleccion).exists():
            raise serializers.ValidationError(
                "Este votante ya está habilitado para esta elección."
            )

        return data