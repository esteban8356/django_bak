from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Votante
from .serializers import VotanteSerializer
from apps.permissions import EsAdmin
'''en estas lineas de codigo en la 12, Solo admin puede habilitar votantes'''
class VotanteViewSet(viewsets.ModelViewSet):
    queryset = Votante.objects.all()
    serializer_class = VotanteSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            
            return [EsAdmin()]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = Votante.objects.all()
        eleccion_id = self.request.query_params.get('eleccion')
        if eleccion_id:
            queryset = queryset.filter(eleccion=eleccion_id)
        return queryset