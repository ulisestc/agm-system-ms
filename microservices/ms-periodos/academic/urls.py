from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import PeriodoViewSet

router = DefaultRouter()
router.register(r"periodos", PeriodoViewSet, basename="periodos")

urlpatterns = [
    path("", include(router.urls)),
]
