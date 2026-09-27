"""Tests for patient CRUD, ownership and security."""
from django.urls import reverse
from rest_framework import status

from apps.accounts.tests import BaseAPITestCase
from apps.patients.models import Patient

LIST_URL = reverse("patient-list")


def detail_url(pk):
    return reverse("patient-detail", kwargs={"pk": pk})


class PatientTests(BaseAPITestCase):
    def setUp(self):
        self.authenticate(email="owner@example.com")
        self.other = self.register_and_login("other@example.com")

    def register_and_login(self, email, password="SecurePass123!", name="Other User"):
        self.register(email=email, password=password, name=name)
        data = self.login(email=email, password=password)
        token = data["access"]
        return token

    # ------------------------------------------------------------------ #
    # Create
    # ------------------------------------------------------------------ #
    def test_create_patient(self):
        payload = {
            "name": "John Doe",
            "age": 34,
            "gender": "male",
            "phone": "+1-555-0100",
            "address": "12 Main St",
        }
        response = self.client.post(LIST_URL, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "John Doe")
        self.assertEqual(response.data["created_by"], "owner@example.com")
        self.assertEqual(response.data["age"], 34)

    def test_create_patient_is_owned_by_request_user(self):
        response = self.client.post(LIST_URL, {"name": "Owned", "age": 20}, format="json")
        patient = Patient.objects.get(pk=response.data["id"])

        self.assertEqual(patient.created_by.email, "owner@example.com")

    def test_create_patient_requires_authentication(self):
        self.client.credentials()
        response = self.client.post(LIST_URL, {"name": "Nope"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_patient_missing_name(self):
        response = self.client.post(LIST_URL, {"age": 30}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)

    def test_create_patient_invalid_age(self):
        response = self.client.post(LIST_URL, {"name": "Bad", "age": -5}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("age", response.data)

    def test_create_patient_invalid_gender(self):
        response = self.client.post(
            LIST_URL, {"name": "Bad", "age": 30, "gender": "robot"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("gender", response.data)

    # ------------------------------------------------------------------ #
    # List
    # ------------------------------------------------------------------ #
    def test_list_returns_only_own_patients(self):
        self.client.post(LIST_URL, {"name": "Mine A", "age": 20}, format="json")
        self.client.post(LIST_URL, {"name": "Mine B", "age": 21}, format="json")

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.other}")
        self.client.post(LIST_URL, {"name": "Theirs", "age": 40}, format="json")

        self.client.credentials(
            HTTP_AUTHORIZATION="Bearer "
            + self.login(email="owner@example.com")["access"]
        )
        response = self.client.get(LIST_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [p["name"] for p in response.data]
        self.assertEqual(sorted(names), ["Mine A", "Mine B"])
        self.assertNotIn("Theirs", names)

    def test_list_requires_authentication(self):
        self.client.credentials()
        response = self.client.get(LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # ------------------------------------------------------------------ #
    # Detail
    # ------------------------------------------------------------------ #
    def test_retrieve_own_patient(self):
        create = self.client.post(LIST_URL, {"name": "Retrieve me", "age": 50}, format="json")
        response = self.client.get(detail_url(create.data["id"]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Retrieve me")

    def test_retrieve_another_users_patient_forbidden(self):
        create = self.client.post(LIST_URL, {"name": "Secret", "age": 50}, format="json")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.other}")
        response = self.client.get(detail_url(create.data["id"]))

        self.assertIn(
            response.status_code,
            (status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND),
        )
        self.assertNotIn("name", response.data if isinstance(response.data, dict) else {})

    def test_retrieve_nonexistent_patient(self):
        response = self.client.get(detail_url(999999))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ------------------------------------------------------------------ #
    # Update
    # ------------------------------------------------------------------ #
    def test_update_own_patient(self):
        create = self.client.post(LIST_URL, {"name": "Old", "age": 30}, format="json")
        response = self.client.put(
            detail_url(create.data["id"]),
            {"name": "New Name", "age": 31, "gender": "female"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "New Name")
        refresh = self.client.get(detail_url(create.data["id"]))
        self.assertEqual(refresh.data["age"], 31)

    def test_partial_update_own_patient(self):
        create = self.client.post(LIST_URL, {"name": "Patch", "age": 30}, format="json")
        response = self.client.patch(
            detail_url(create.data["id"]), {"address": "New address"}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["address"], "New address")
        self.assertEqual(response.data["name"], "Patch")

    def test_update_another_users_patient_forbidden(self):
        create = self.client.post(LIST_URL, {"name": "Victim", "age": 30}, format="json")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.other}")
        response = self.client.put(
            detail_url(create.data["id"]), {"name": "Hacked", "age": 30}, format="json"
        )

        self.assertIn(
            response.status_code,
            (status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND),
        )
        self.client.credentials(
            HTTP_AUTHORIZATION="Bearer " + self.login(email="owner@example.com")["access"]
        )
        self.assertEqual(
            self.client.get(detail_url(create.data["id"])).data["name"], "Victim"
        )

    # ------------------------------------------------------------------ #
    # Delete
    # ------------------------------------------------------------------ #
    def test_delete_own_patient(self):
        create = self.client.post(LIST_URL, {"name": "Delete me", "age": 30}, format="json")
        response = self.client.delete(detail_url(create.data["id"]))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Patient.objects.filter(pk=create.data["id"]).exists())

    def test_delete_another_users_patient_forbidden(self):
        create = self.client.post(LIST_URL, {"name": "Keep me", "age": 30}, format="json")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.other}")
        response = self.client.delete(detail_url(create.data["id"]))

        self.assertIn(
            response.status_code,
            (status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND),
        )
        self.assertTrue(Patient.objects.filter(pk=create.data["id"]).exists())

    def test_delete_nonexistent_patient(self):
        response = self.client.delete(detail_url(999999))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_invalid_patient_id_returns_json_not_html(self):
        response = self.client.get("/api/patients/not-a-number/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response["Content-Type"], "application/json")
        self.assertIn("detail", response.data)
