'''from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Voto
from .serializers import VotoSerializer
from apps.permissions import EsVotante'''

'''Por aca protegemos el endpoint de votos
 Solo votantes autenticados pueden votar'''
'''
class VotoViewSet(viewsets.ModelViewSet):
    queryset = Voto.objects.all()
    serializer_class = VotoSerializer
    http_method_names = ['get', 'post']

    def get_permissions(self):
       
        return [EsVotante()]

    def get_queryset(self):
        return Voto.objects.filter(usuario=self.request.user)
    '''

from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Count
from .models import Voto
from .serializers import VotoSerializer
from apps.elecciones.models import Eleccion
from apps.candidatos.models import Candidato
from apps.votantes.models import Votante

class VotoViewSet(viewsets.ModelViewSet):
    queryset = Voto.objects.all()
    serializer_class = VotoSerializer
    http_method_names = ['get', 'post']

    def get_permissions(self):
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        return Voto.objects.filter(usuario=self.request.user)


class ResultadosView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, eleccion_id):
        # Verificar que la elección existe
        try:
            eleccion = Eleccion.objects.get(id=eleccion_id)
        except Eleccion.DoesNotExist:
            return Response({'error': 'Elección no encontrada'}, status=404)

        # Contar votos por candidato
        candidatos = Candidato.objects.filter(eleccion=eleccion)
        total_votos = Voto.objects.filter(eleccion=eleccion).count()
        total_habilitados = Votante.objects.filter(eleccion=eleccion, habilitado=True).count()

        resultados = []
        for candidato in candidatos:
            votos_candidato = Voto.objects.filter(
                eleccion=eleccion,
                candidato=candidato
            ).count()

            porcentaje = round((votos_candidato / total_votos * 100), 2) if total_votos > 0 else 0

            resultados.append({
                'candidato_id': candidato.id,
                'candidato_nombre': candidato.nombre,
                'votos': votos_candidato,
                'porcentaje': porcentaje,
            })

        # Ordenar de mayor a menor votos
        resultados.sort(key=lambda x: x['votos'], reverse=True)

        return Response({
            'eleccion': eleccion.nombre,
            'estado': eleccion.estado,
            'total_votos_emitidos': total_votos,
            'total_votantes_habilitados': total_habilitados,
            'participacion': round((total_votos / total_habilitados * 100), 2) if total_habilitados > 0 else 0,
            'resultados': resultados,
        })