"""Patient <-> Doctor mapping with ownership and uniqueness guarantees."""
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from apps.doctors.models import Doctor
from apps.patients.models import Patient


def validate_patient_owner(patient, user):
    """Ensure ``user`` is allowed to act on ``patient``."""
    if patient.created_by_id != user.id:
        raise ValidationError("You do not have permission to act on this patient.")


class PatientDoctorMapping(models.Model):
    """Assigns a doctor to a patient. Unique per (patient, doctor) pair."""

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name="doctor_mappings",
    )
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name="patient_mappings",
    )
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="mappings_created",
        help_text="User that created this mapping (audit trail).",
    )
    notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["patient", "doctor"],
                name="unique_patient_doctor_mapping",
            )
        ]
        indexes = [
            models.Index(fields=["patient", "doctor"], name="mapping_patient_doctor_idx"),
            models.Index(fields=["-created_at"], name="mapping_created_idx"),
        ]

    def __str__(self):
        return f"{self.patient_id} -> {self.doctor_id}"

    def clean(self):
        super().clean()
        if self.patient_id and self.assigned_by_id:
            validate_patient_owner(self.patient, self.assigned_by)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
