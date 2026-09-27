"""Tests for patient-doctor mapping endpoints."""
from django.urls import reverse
from rest_framework import status

from apps.accounts.tests import BaseAPITestCase
from apps.mappings.models import PatientDoctorMapping

LIST_URL = reverse("mappings:mapping-list")
DETAIL_URL = "mappings:mapping-detail"


def detail_url(pk):
    return reverse(DETAIL_URL, kwargs={"pk": pk})


class MappingTests(BaseAPITestCase):
    def setUp(self):
        self.authenticate(email="mapper@example.com")
        patient = self.client.post(
            reverse("patient-list"),
            {"name": "Mapping Patient", "age": 45},
            format="json",
        ).data
        self.patient_id = patient["id"]
        doctor = self.client.post(
            reverse("doctor-list"),
            {"name": "Asha Rao", "specialization": "Neurology", "email": "asha@clinic.com"},
            format="json",
        ).data
        self.doctor_id = doctor["id"]

        # a second user with their own patient + doctor (for isolation tests)
        self.other_token = self.register_and_login("other-mapper@example.com")

    def register_and_login(self, email, password="SecurePass123!"):
        self.register(email=email, password=password)
        return self.login(email=email, password=password)["access"]

    def use_other_user(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.other_token}")

    def use_owner(self):
        self.client.credentials(
            HTTP_AUTHORIZATION="Bearer " + self.login(email="mapper@example.com")["access"]
        )

    # ------------------------------------------------------------------ #
    # Create
    # ------------------------------------------------------------------ #
    def test_create_mapping(self):
        response = self.client.post(
            LIST_URL, {"patient": self.patient_id, "doctor": self.doctor_id}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["patient"], self.patient_id)
        self.assertEqual(response.data["doctor"], self.doctor_id)
        self.assertEqual(response.data["assigned_by"], "mapper@example.com")

    def test_duplicate_mapping_rejected(self):
        self.client.post(
            LIST_URL, {"patient": self.patient_id, "doctor": self.doctor_id}, format="json"
        )
        response = self.client.post(
            LIST_URL, {"patient": self.patient_id, "doctor": self.doctor_id}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_mapping_invalid_patient(self):
        response = self.client.post(
            LIST_URL, {"patient": 999999, "doctor": self.doctor_id}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("patient", response.data)

    def test_mapping_invalid_doctor(self):
        response = self.client.post(
            LIST_URL, {"patient": self.patient_id, "doctor": 999999}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("doctor", response.data)

    def test_mapping_missing_fields(self):
        response = self.client.post(LIST_URL, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("patient", response.data)
        self.assertIn("doctor", response.data)

    def test_cannot_map_another_users_patient(self):
        self.use_other_user()
        other_patient = self.client.post(
            reverse("patient-list"), {"name": "Their Patient", "age": 30}, format="json"
        ).data
        self.use_owner()

        response = self.client.post(
            LIST_URL, {"patient": other_patient["id"], "doctor": self.doctor_id}, format="json"
        )
        self.assertIn(
            response.status_code,
            (status.HTTP_400_BAD_REQUEST, status.HTTP_403_FORBIDDEN),
        )
        self.assertFalse(
            PatientDoctorMapping.objects.filter(patient_id=other_patient["id"]).exists()
        )

    def test_create_mapping_requires_authentication(self):
        self.client.credentials()
        response = self.client.post(
            LIST_URL, {"patient": self.patient_id, "doctor": self.doctor_id}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # ------------------------------------------------------------------ #
    # List
    # ------------------------------------------------------------------ #
    def test_list_mappings(self):
        self.client.post(
            LIST_URL, {"patient": self.patient_id, "doctor": self.doctor_id}, format="json"
        )
        response = self.client.get(LIST_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["patient_name"], "Mapping Patient")
        self.assertEqual(response.data[0]["doctor_name"], "Asha Rao")

    def test_list_mappings_excludes_other_users(self):
        self.client.post(
            LIST_URL, {"patient": self.patient_id, "doctor": self.doctor_id}, format="json"
        )
        self.use_other_user()
        other_patient = self.client.post(
            reverse("patient-list"), {"name": "Other Patient", "age": 30}, format="json"
        ).data
        other_doctor = self.client.post(
            reverse("doctor-list"),
            {"name": "Ravi Kumar", "specialization": "Ortho", "email": "ravi@clinic.com"},
            format="json",
        ).data
        self.client.post(
            LIST_URL, {"patient": other_patient["id"], "doctor": other_doctor["id"]},
            format="json",
        )

        response = self.client.get(LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["patient_name"], "Other Patient")

    def test_list_requires_authentication(self):
        self.client.credentials()
        response = self.client.get(LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # ------------------------------------------------------------------ #
    # Doctors assigned to a patient
    # ------------------------------------------------------------------ #
    def test_get_doctors_for_patient(self):
        self.client.post(
            LIST_URL, {"patient": self.patient_id, "doctor": self.doctor_id}, format="json"
        )
        response = self.client.get(detail_url(self.patient_id))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Asha Rao")
        self.assertEqual(response.data[0]["specialization"], "Neurology")
        self.assertEqual(response.data[0]["mapping_id"],
                         PatientDoctorMapping.objects.first().id)

    def test_get_doctors_for_patient_with_no_mappings(self):
        response = self.client.get(detail_url(self.patient_id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_get_doctors_for_nonexistent_patient(self):
        response = self.client.get(detail_url(999999))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_doctors_for_another_users_patient_forbidden(self):
        self.use_other_user()
        other_patient = self.client.post(
            reverse("patient-list"), {"name": "Hidden", "age": 22}, format="json"
        ).data
        self.use_owner()
        response = self.client.get(detail_url(other_patient["id"]))

        self.assertIn(
            response.status_code,
            (status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND),
        )

    # ------------------------------------------------------------------ #
    # Delete
    # ------------------------------------------------------------------ #
    def test_delete_mapping(self):
        created = self.client.post(
            LIST_URL, {"patient": self.patient_id, "doctor": self.doctor_id}, format="json"
        ).data
        response = self.client.delete(detail_url(created["id"]))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(PatientDoctorMapping.objects.filter(pk=created["id"]).exists())

    def test_delete_nonexistent_mapping(self):
        response = self.client.delete(detail_url(999999))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_another_users_mapping_forbidden(self):
        created = self.client.post(
            LIST_URL, {"patient": self.patient_id, "doctor": self.doctor_id}, format="json"
        ).data
        self.use_other_user()
        response = self.client.delete(detail_url(created["id"]))

        self.assertIn(
            response.status_code,
            (status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND),
        )
        self.assertTrue(PatientDoctorMapping.objects.filter(pk=created["id"]).exists())

    def test_delete_requires_authentication(self):
        created = self.client.post(
            LIST_URL, {"patient": self.patient_id, "doctor": self.doctor_id}, format="json"
        ).data
        self.client.credentials()
        response = self.client.delete(detail_url(created["id"]))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
