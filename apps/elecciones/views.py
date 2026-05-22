'''from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Eleccion
from .serializers import EleccionSerializer
from apps.permissions import EsAdmin
#en este codigo aplicamos los permisos en las vistas, provenientes de permissions.py
# Solo admin puede crear, editar y eliminar
# Cualquier usuario autenticado puede ver

class EleccionViewSet(viewsets.ModelViewSet):
    queryset = Eleccion.objects.all()
    serializer_class = EleccionSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            
            return [EsAdmin()]
       
        return [IsAuthenticated()]
'''

from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone
from .models import Eleccion
from .serializers import EleccionSerializer
from apps.permissions import EsAdmin

class EleccionViewSet(viewsets.ModelViewSet):
    queryset = Eleccion.objects.all()
    serializer_class = EleccionSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [EsAdmin()]
        return [permissions.IsAuthenticated()]

    @action(detail=True, methods=['post'], permission_classes=[EsAdmin])
    def cerrar(self, request, pk=None):
        """
        Cierra manualmente una elección
        POST /api/elecciones/1/cerrar/
        """
        try:
            eleccion = self.get_object()

            if eleccion.estado == 'cerrada':
                return Response(
                    {'error': 'La elección ya está cerrada'},
                    status=400
                )

            eleccion.estado = 'cerrada'
            eleccion.save()

            return Response({
                'mensaje': f'Elección "{eleccion.nombre}" cerrada exitosamente',
                'estado': eleccion.estado
            })
        except Exception as e:
            return Response({'error': str(e)}, status=500)


class CerrarEleccionesVencidasView(APIView):
    """
    Cierra automáticamente todas las elecciones
    cuya fecha de cierre ya pasó
    """
    permission_classes = [EsAdmin]

    def post(self, request):
        ahora = timezone.now()

        elecciones_vencidas = Eleccion.objects.filter(
            estado='activa',
            fecha_cierre__lt=ahora
        )

        cantidad = elecciones_vencidas.count()
        elecciones_vencidas.update(estado='cerrada')

        return Response({
            'mensaje': f'{cantidad} elección(es) cerrada(s) automáticamente',
            'cerradas': cantidad
        })