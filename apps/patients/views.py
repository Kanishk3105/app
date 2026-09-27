"""Patient CRUD. Records are strictly scoped to the authenticated user."""
from rest_framework import status
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.patients.models import Patient
from apps.patients.serializers import PatientSerializer


class PatientViewSet(ModelViewSet):
    """POST/GET/PUT/DELETE ``/api/patients/`` and ``/api/patients/<id>/``.

    Every query is filtered by ``created_by == request.user`` so one user can
    never read, update or delete another user's patient records.
    """

    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "put", "patch", "delete", "head", "options"]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Patient.objects.none()
        return Patient.objects.filter(created_by=self.request.user).select_related("created_by")

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def get_object(self):
        pk = self.kwargs.get("pk")
        try:
            patient = Patient.objects.filter(pk=pk).first()
        except (TypeError, ValueError):
            patient = None

        if patient is None:
            raise NotFound("Patient not found.")
        if patient.created_by_id != self.request.user.id:
            raise PermissionDenied("You do not have permission to access this patient record.")
        return patient

    def destroy(self, request, *args, **kwargs):
        patient = self.get_object()
        patient.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
