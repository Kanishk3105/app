"""Endpoints for assigning doctors to patients.

Route summary (see README for the reasoning):

* ``GET/POST    /api/mappings/``          - list / create mappings
* ``GET         /api/mappings/<patient_id>/`` - doctors assigned to a patient
* ``DELETE      /api/mappings/<id>/``     - remove a mapping
"""
from rest_framework import status
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.generics import ListCreateAPIView, GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.doctors.models import Doctor
from apps.doctors.serializers import DoctorSerializer
from apps.mappings.models import PatientDoctorMapping
from apps.mappings.serializers import MappingSerializer
from apps.patients.models import Patient


class MappingListCreateView(ListCreateAPIView):
    """GET /api/mappings/ and POST /api/mappings/."""

    serializer_class = MappingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return PatientDoctorMapping.objects.none()
        return PatientDoctorMapping.objects.filter(
            patient__created_by=self.request.user
        ).select_related("patient", "doctor", "assigned_by")

    def perform_create(self, serializer):
        serializer.save(assigned_by=self.request.user)


class MappingPatientDoctorsView(GenericAPIView):
    """GET /api/mappings/<patient_id>/ - doctors assigned to a patient.
    DELETE /api/mappings/<id>/ - remove a mapping."""

    permission_classes = [IsAuthenticated]
    queryset = PatientDoctorMapping.objects.all()

    def get_serializer_class(self):
        return MappingSerializer

    def _get_owned_patient(self, patient_id):
        patient = Patient.objects.filter(pk=patient_id).first()
        if patient is None:
            raise NotFound("Patient not found.")
        if patient.created_by_id != self.request.user.id:
            raise PermissionDenied("You do not have permission to access this patient record.")
        return patient

    def get(self, request, *args, **kwargs):
        patient = self._get_owned_patient(kwargs["pk"])
        mappings = PatientDoctorMapping.objects.filter(patient=patient).select_related("doctor")
        doctors = [m.doctor for m in mappings]
        payload = []
        for mapping, doctor in zip(mappings, doctors):
            payload.append({"mapping_id": mapping.id, **DoctorSerializer(doctor).data})
        return Response(payload, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        mapping = PatientDoctorMapping.objects.filter(pk=kwargs["pk"]).first()
        if mapping is None:
            raise NotFound("Mapping not found.")
        if mapping.patient.created_by_id != request.user.id:
            raise PermissionDenied("You do not have permission to modify this mapping.")
        mapping.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
