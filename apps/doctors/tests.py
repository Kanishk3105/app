"""Tests for doctor CRUD endpoints."""
from django.urls import reverse
from rest_framework import status

from apps.accounts.tests import BaseAPITestCase
from apps.doctors.models import Doctor

LIST_URL = reverse("doctor-list")


def detail_url(pk):
    return reverse("doctor-detail", kwargs={"pk": pk})


class DoctorTests(BaseAPITestCase):
    def setUp(self):
        self.authenticate(email="doctor-owner@example.com")

    def create_doctor(self, **overrides):
        payload = {
            "name": "Priya Sharma",
            "specialization": "Cardiology",
            "email": "priya@clinic.com",
            "phone": "+1-555-0199",
            "qualification": "MD",
        }
        payload.update(overrides)
        return self.client.post(LIST_URL, payload, format="json")

    # ------------------------------------------------------------------ #
    # Create
    # ------------------------------------------------------------------ #
    def test_create_doctor(self):
        response = self.create_doctor()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "Priya Sharma")
        self.assertEqual(response.data["specialization"], "Cardiology")
        self.assertEqual(response.data["created_by"], "doctor-owner@example.com")
        self.assertNotIn("password", response.data)

    def test_create_doctor_requires_authentication(self):
        self.client.credentials()
        response = self.client.post(
            LIST_URL, {"name": "X", "specialization": "Y"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_doctor_missing_specialization(self):
        response = self.client.post(LIST_URL, {"name": "No Spec"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("specialization", response.data)

    def test_create_doctor_duplicate_email_rejected(self):
        self.create_doctor(email="dup@clinic.com")
        response = self.create_doctor(name="Another", email="dup@clinic.com")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_create_doctor_invalid_email(self):
        response = self.create_doctor(email="not-an-email")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    # ------------------------------------------------------------------ #
    # List / retrieve
    # ------------------------------------------------------------------ #
    def test_list_doctors(self):
        self.create_doctor()
        self.create_doctor(name="Rahul Verma", specialization="Dermatology",
                           email="rahul@clinic.com")
        response = self.client.get(LIST_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_list_requires_authentication(self):
        self.client.credentials()
        response = self.client.get(LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_doctor(self):
        created = self.create_doctor()
        response = self.client.get(detail_url(created.data["id"]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["specialization"], "Cardiology")

    def test_retrieve_nonexistent_doctor(self):
        response = self.client.get(detail_url(999999))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_invalid_doctor_id_returns_json(self):
        response = self.client.get("/api/doctors/abc/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response["Content-Type"], "application/json")

    # ------------------------------------------------------------------ #
    # Update
    # ------------------------------------------------------------------ #
    def test_update_doctor(self):
        created = self.create_doctor()
        response = self.client.put(
            detail_url(created.data["id"]),
            {
                "name": "Priya Sharma",
                "specialization": "Cardiology",
                "email": "priya@clinic.com",
                "years_of_experience": 12,
                "is_available": False,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["years_of_experience"], 12)
        self.assertFalse(response.data["is_available"])

    def test_partial_update_doctor(self):
        created = self.create_doctor()
        response = self.client.patch(
            detail_url(created.data["id"]), {"phone": "+1-555-0001"}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["phone"], "+1-555-0001")

    def test_update_nonexistent_doctor(self):
        response = self.client.put(
            detail_url(999999),
            {"name": "Ghost", "specialization": "None"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ------------------------------------------------------------------ #
    # Delete
    # ------------------------------------------------------------------ #
    def test_delete_doctor(self):
        created = self.create_doctor()
        response = self.client.delete(detail_url(created.data["id"]))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Doctor.objects.filter(pk=created.data["id"]).exists())

    def test_delete_nonexistent_doctor(self):
        response = self.client.delete(detail_url(999999))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_requires_authentication(self):
        created = self.create_doctor()
        self.client.credentials()
        response = self.client.delete(detail_url(created.data["id"]))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(Doctor.objects.filter(pk=created.data["id"]).exists())
