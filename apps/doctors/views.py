"""Doctor CRUD. Doctors are a shared directory for all authenticated users."""
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from apps.doctors.models import Doctor
from apps.doctors.serializers import DoctorSerializer


class DoctorViewSet(ModelViewSet):
    """POST/GET/PUT/DELETE ``/api/doctors/`` and ``/api/doctors/<id>/``."""

    serializer_class = DoctorSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "put", "patch", "delete", "head", "options"]
    queryset = Doctor.objects.all().select_related("created_by")

    def get_queryset(self):
        return Doctor.objects.all().select_related("created_by")

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def get_object(self):
        pk = self.kwargs.get("pk")
        try:
            doctor = Doctor.objects.filter(pk=pk).first()
        except (TypeError, ValueError):
            doctor = None
        if doctor is None:
            raise NotFound("Doctor not found.")
        return doctor
