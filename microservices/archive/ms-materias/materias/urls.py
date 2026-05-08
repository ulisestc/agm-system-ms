from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import MateriaViewSet

router = DefaultRouter()
router.register(r"materias", MateriaViewSet, basename="materias")

urlpatterns = [
    path("", include(router.urls)),
]
