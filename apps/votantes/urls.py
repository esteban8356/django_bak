from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'votantes', views.VotanteViewSet)

urlpatterns = router.urls