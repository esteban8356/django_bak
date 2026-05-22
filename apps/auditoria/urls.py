from django.urls import path
from . import views

urlpatterns = [
    path(
        'auditoria/eleccion/<int:eleccion_id>/',
        views.AuditoriaEleccionView.as_view(),
        name='auditoria-eleccion'
    ),
    path(
        'auditoria/general/',
        views.AuditoriaGeneralView.as_view(),
        name='auditoria-general'
    ),
]