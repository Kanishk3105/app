"""Serializers for creating and reading patient-doctor mappings."""
from rest_framework import serializers

from apps.doctors.models import Doctor
from apps.doctors.serializers import DoctorSerializer
from apps.mappings.models import PatientDoctorMapping
from apps.patients.models import Patient
from apps.patients.serializers import PatientSerializer


class MappingSerializer(serializers.ModelSerializer):
    """Create/read a mapping. ``patient`` and ``doctor`` are primary keys."""

    doctor_detail = DoctorSerializer(source="doctor", read_only=True)
    patient_detail = PatientSerializer(source="patient", read_only=True)
    assigned_by = serializers.EmailField(source="assigned_by.email", read_only=True)
    patient_name = serializers.CharField(source="patient.name", read_only=True)
    doctor_name = serializers.CharField(source="doctor.name", read_only=True)
    doctor_specialization = serializers.CharField(
        source="doctor.specialization", read_only=True
    )

    class Meta:
        model = PatientDoctorMapping
        fields = (
            "id",
            "patient",
            "patient_name",
            "doctor",
            "doctor_name",
            "doctor_specialization",
            "doctor_detail",
            "patient_detail",
            "notes",
            "assigned_by",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "assigned_by", "created_at", "updated_at")

    def validate_patient(self, patient):
        user = self.context["request"].user
        if patient.created_by_id != user.id:
            raise serializers.ValidationError("You do not have access to this patient.")
        return patient

    def validate_doctor(self, doctor):
        if not Doctor.objects.filter(pk=doctor.pk).exists():
            raise serializers.ValidationError("Doctor not found.")
        return doctor

    def validate(self, attrs):
        patient = attrs.get("patient") or (self.instance.patient if self.instance else None)
        doctor = attrs.get("doctor") or (self.instance.doctor if self.instance else None)
        if patient and doctor:
            duplicate = PatientDoctorMapping.objects.filter(patient=patient, doctor=doctor)
            if self.instance:
                duplicate = duplicate.exclude(pk=self.instance.pk)
            if duplicate.exists():
                raise serializers.ValidationError(
                    {"doctor": "This doctor is already assigned to this patient."}
                )
        return attrs
