"""Doctor model. Doctors form a shared directory visible to every authenticated user."""
from django.conf import settings
from django.db import models
from django.utils.text import slugify


class Doctor(models.Model):
    """A doctor that can be mapped to patients."""

    name = models.CharField(max_length=150)
    specialization = models.CharField(
        max_length=120,
        help_text="e.g. Cardiology, Dermatology, General Practice.",
    )
    qualification = models.CharField(max_length=120, blank=True, default="")
    email = models.EmailField(blank=True, default="")
    phone = models.CharField(max_length=20, blank=True, default="")
    clinic_address = models.TextField(blank=True, default="")
    years_of_experience = models.PositiveIntegerField(null=True, blank=True)
    is_available = models.BooleanField(default=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="doctors_created",
        help_text="User that registered this doctor (audit trail).",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["specialization"], name="doctor_specialization_idx"),
            models.Index(fields=["name"], name="doctor_name_idx"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["email"],
                condition=~models.Q(email=""),
                name="doctor_unique_email_when_set",
            )
        ]

    def __str__(self):
        return f"Dr. {self.name} - {self.specialization}"

    @property
    def slug(self):
        return slugify(f"{self.name}-{self.specialization}")
