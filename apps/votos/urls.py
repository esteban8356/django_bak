'''from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'votos', views.VotoViewSet)

urlpatterns = router.urls'''

from rest_framework import routers
from django.urls import path
from . import views

router = routers.DefaultRouter()
router.register(r'votos', views.VotoViewSet)

urlpatterns = router.urls + [
    path('resultados/<int:eleccion_id>/', views.ResultadosView.as_view(), name='resultados'),
]