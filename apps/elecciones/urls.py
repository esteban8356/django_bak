'''from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'elecciones', views.EleccionViewSet)

urlpatterns = router.urls'''

from rest_framework import routers
from django.urls import path
from . import views

router = routers.DefaultRouter()
router.register(r'elecciones', views.EleccionViewSet)

urlpatterns = router.urls + [
    path(
        'elecciones/cerrar-vencidas/',
        views.CerrarEleccionesVencidasView.as_view(),
        name='cerrar-vencidas'
    ),
]