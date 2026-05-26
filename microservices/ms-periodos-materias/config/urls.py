from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path

from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import AllowAny

@authentication_classes([])
@permission_classes([AllowAny])
def health_check(_request):
    return JsonResponse({"success": True, "message": "ms-periodos-materias is running"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", health_check),
    path("api/", include("academic.urls")),
]
