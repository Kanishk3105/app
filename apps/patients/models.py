"""Patient model. Patients are private to the user who created them."""
from django.conf import settings
from django.db import models


class Patient(models.Model):
    """A healthcare patient owned by exactly one user."""

    class Gender(models.TextChoices):
        MALE = "male", "Male"
        FEMALE = "female", "Female"
        OTHER = "other", "Other"
        PREFER_NOT_TO_SAY = "prefer_not_to_say", "Prefer not to say"

    name = models.CharField(max_length=150)
    date_of_birth = models.DateField(null=True, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    gender = models.CharField(
        max_length=20,
        choices=Gender.choices,
        default=Gender.PREFER_NOT_TO_SAY,
    )
    phone = models.CharField(max_length=20, blank=True, default="")
    email = models.EmailField(blank=True, default="")
    address = models.TextField(blank=True, default="")
    blood_group = models.CharField(max_length=5, blank=True, default="")
    allergies = models.TextField(blank=True, default="", help_text="Known allergies.")
    medical_history = models.TextField(blank=True, default="", help_text="Relevant medical history.")

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="patients",
        help_text="User that created this patient record.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["created_by", "-created_at"], name="patient_owner_created_idx"),
            models.Index(fields=["name"], name="patient_name_idx"),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(age__isnull=True) | models.Q(age__gte=0),
                name="patient_age_non_negative",
            )
        ]

    def __str__(self):
        return f"{self.name} ({self.pk})"
