from rest_framework import serializers
from .models import Eleccion

class EleccionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Eleccion
        fields = '__all__'

    def validate(self, data):
        if data['fecha_inicio'] >= data['fecha_cierre']:
            raise serializers.ValidationError(
                "La fecha de inicio debe ser anterior a la fecha de cierre."
            )
        return data