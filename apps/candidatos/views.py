from django.shortcuts import render
'''from rest_framework import viewsets
from .models import candidato
from .serializers import candidatoSerializer

# Create your views here.

class candidatoViewSet(viewsets.ModelViewSet):
    query = candidato.objects.all()
    serializer_class = candidatoSerializer'''

'''from rest_framework import viewsets
from .models import Candidato
from .serializers import CandidatoSerializer

class CandidatoViewSet(viewsets.ModelViewSet):
    queryset = Candidato.objects.all()
    serializer_class = CandidatoSerializer

    def get_queryset(self):
        queryset = Candidato.objects.all()
        eleccion_id = self.request.query_params.get('eleccion')
        if eleccion_id:
            queryset = queryset.filter(eleccion=eleccion_id)
        return queryset'''

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Candidato
from .serializers import CandidatoSerializer
from apps.permissions import EsAdmin

class CandidatoViewSet(viewsets.ModelViewSet):
    queryset = Candidato.objects.all()
    serializer_class = CandidatoSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [EsAdmin()]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = Candidato.objects.all()
        eleccion_id = self.request.query_params.get('eleccion')
        if eleccion_id:
            queryset = queryset.filter(eleccion=eleccion_id)
        return queryset