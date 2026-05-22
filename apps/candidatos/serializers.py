'''from rest_framework import serializers
from .models import candidato

class candidatoSerializer(serializers.ModelSerializer):
    class Meta:
        model = candidato
        fields = '__all__'
'''

from rest_framework import serializers
from .models import Candidato

class CandidatoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Candidato
        fields = '__all__'

    def validate(self, data):
        eleccion = data.get('eleccion')
        if eleccion and eleccion.estado == 'cerrada':
            raise serializers.ValidationError(
                "No se pueden agregar candidatos a una elección cerrada."
            )
        return data