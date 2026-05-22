from django.shortcuts import render

# Create your views here.

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.utils import timezone
from apps.elecciones.models import Eleccion
from apps.candidatos.models import Candidato
from apps.votantes.models import Votante
from apps.votos.models import Voto
from apps.permissions import EsAdmin


class AuditoriaEleccionView(APIView):
    """
    Reporte completo de auditoría de una elección
    GET /api/auditoria/eleccion/1/
    """
    permission_classes = [EsAdmin]

    def get(self, request, eleccion_id):
        try:
            eleccion = Eleccion.objects.get(id=eleccion_id)
        except Eleccion.DoesNotExist:
            return Response({'error': 'Elección no encontrada'}, status=404)

        total_habilitados = Votante.objects.filter(
            eleccion=eleccion,
            habilitado=True
        ).count()

        total_votos = Voto.objects.filter(eleccion=eleccion).count()

        participacion = round(
            (total_votos / total_habilitados * 100), 2
        ) if total_habilitados > 0 else 0

        sin_votar = total_habilitados - total_votos

        # Votos por candidato
        candidatos = Candidato.objects.filter(eleccion=eleccion)
        detalle_candidatos = []
        for candidato in candidatos:
            votos = Voto.objects.filter(
                eleccion=eleccion,
                candidato=candidato
            ).count()
            detalle_candidatos.append({
                'candidato': candidato.nombre,
                'votos': votos,
                'porcentaje': round((votos / total_votos * 100), 2) if total_votos > 0 else 0
            })

        detalle_candidatos.sort(key=lambda x: x['votos'], reverse=True)

        return Response({
            'eleccion': eleccion.nombre,
            'estado': eleccion.estado,
            'fecha_inicio': eleccion.fecha_inicio,
            'fecha_cierre': eleccion.fecha_cierre,
            'total_votantes_habilitados': total_habilitados,
            'total_votos_emitidos': total_votos,
            'total_sin_votar': sin_votar,
            'participacion_porcentaje': participacion,
            'detalle_por_candidato': detalle_candidatos,
        })


class AuditoriaGeneralView(APIView):
    """
    Reporte general de todas las elecciones
    GET /api/auditoria/general/
    """
    permission_classes = [EsAdmin]

    def get(self, request):
        elecciones = Eleccion.objects.all()
        reporte = []

        for eleccion in elecciones:
            total_habilitados = Votante.objects.filter(
                eleccion=eleccion,
                habilitado=True
            ).count()

            total_votos = Voto.objects.filter(eleccion=eleccion).count()

            participacion = round(
                (total_votos / total_habilitados * 100), 2
            ) if total_habilitados > 0 else 0

            reporte.append({
                'eleccion_id': eleccion.id,
                'eleccion': eleccion.nombre,
                'estado': eleccion.estado,
                'total_habilitados': total_habilitados,
                'total_votos': total_votos,
                'participacion': participacion,
            })

        return Response({
            'total_elecciones': elecciones.count(),
            'reporte': reporte
        })
