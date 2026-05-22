from rest_framework import serializers
from .models import Voto
from apps.votantes.models import Votante
from django.utils import timezone

class VotoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Voto
        fields = '__all__'
        read_only_fields = ['usuario']

    def validate(self, data):
        eleccion = data.get('eleccion')
        candidato = data.get('candidato')
        usuario = self.context['request'].user
        
        #cierre automatico si la fecha ya paso
        ahora = timezone.now()
        if eleccion.estado == 'activa' and ahora > eleccion.fecha_cierre:
            eleccion.estado = 'cerrada'
            eleccion.save()

        # Verificar que la elección esté activa
        if eleccion.estado != 'activa':
            raise serializers.ValidationError(
                "Solo se puede votar en elecciones activas."
            )

        # Verificar que la elección esté dentro del rango de fechas
        ahora = timezone.now()
        if ahora < eleccion.fecha_inicio or ahora > eleccion.fecha_cierre:
            raise serializers.ValidationError(
                "La elección no está dentro del rango de fechas permitido."
            )

        # Verificar que el candidato pertenezca a la elección
        if candidato.eleccion != eleccion:
            raise serializers.ValidationError(
                "El candidato no pertenece a esta elección."
            )

        # Verificar que el votante esté habilitado
        if not Votante.objects.filter(
            usuario=usuario,
            eleccion=eleccion,
            habilitado=True
        ).exists():
            raise serializers.ValidationError(
                "No estás habilitado para votar en esta elección."
            )

        # Verificar que no haya votado antes
        if Voto.objects.filter(usuario=usuario, eleccion=eleccion).exists():
            raise serializers.ValidationError(
                "Ya emitiste tu voto en esta elección."
            )

        return data

    def create(self, validated_data):
        validated_data['usuario'] = self.context['request'].user
        return super().create(validated_data)