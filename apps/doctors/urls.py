from django.urls import include, path
from rest_framework.routers import SimpleRouter

from apps.doctors.views import DoctorViewSet

router = SimpleRouter()
router.register(r"doctors", DoctorViewSet, basename="doctor")

urlpatterns = [
    path("", include(router.urls)),
]
