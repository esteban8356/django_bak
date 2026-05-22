from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'candidatos', views.CandidatoViewSet)

urlpatterns = router.urls