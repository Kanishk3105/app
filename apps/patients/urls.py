from django.urls import include, path
from rest_framework.routers import SimpleRouter

from apps.patients.views import PatientViewSet

router = SimpleRouter()
router.register(r"patients", PatientViewSet, basename="patient")

urlpatterns = [
    path("", include(router.urls)),
]
