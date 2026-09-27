from rest_framework import serializers

from apps.doctors.models import Doctor


class DoctorSerializer(serializers.ModelSerializer):
    """Serializer for doctors. ``created_by`` is filled from the request."""

    created_by = serializers.EmailField(source="created_by.email", read_only=True)

    class Meta:
        model = Doctor
        fields = (
            "id",
            "name",
            "specialization",
            "qualification",
            "email",
            "phone",
            "clinic_address",
            "years_of_experience",
            "is_available",
            "created_by",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_by", "created_at", "updated_at")

    def validate_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Name must not be blank.")
        return value

    def validate_specialization(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Specialization must not be blank.")
        return value

    def validate_email(self, value):
        value = value.strip().lower()
        if value and Doctor.objects.filter(email__iexact=value).exclude(
            pk=self.instance.pk if self.instance else None
        ).exists():
            raise serializers.ValidationError("A doctor with this email already exists.")
        return value

    def validate_years_of_experience(self, value):
        if value is not None and value > 60:
            raise serializers.ValidationError("Years of experience looks invalid.")
        return value
