from rest_framework import serializers

from apps.patients.models import Patient


class PatientSerializer(serializers.ModelSerializer):
    """Serializer for patient records. ``created_by`` is always the request user."""

    created_by = serializers.EmailField(source="created_by.email", read_only=True)
    age = serializers.IntegerField(required=False, allow_null=True, min_value=0, max_value=150)

    class Meta:
        model = Patient
        fields = (
            "id",
            "name",
            "date_of_birth",
            "age",
            "gender",
            "phone",
            "email",
            "address",
            "blood_group",
            "allergies",
            "medical_history",
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

    def validate_email(self, value):
        return value.strip().lower()
