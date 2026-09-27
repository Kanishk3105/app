"""Tests for registration, login and JWT authentication."""
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()

REGISTER_URL = reverse("accounts:register")
LOGIN_URL = reverse("accounts:login")
REFRESH_URL = reverse("accounts:token_refresh")
ME_URL = reverse("accounts:me")
PATIENTS_URL = reverse("patient-list")


class BaseAPITestCase(APITestCase):
    """Shared helpers: register, log in and authenticate a client."""

    def register(self, email="user@example.com", password="SecurePass123!", name="Test User"):
        response = self.client.post(
            REGISTER_URL,
            {"name": name, "email": email, "password": password},
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED, response.data
        return response.data["user"]

    def login(self, email="user@example.com", password="SecurePass123!"):
        response = self.client.post(
            LOGIN_URL, {"email": email, "password": password}, format="json"
        )
        assert response.status_code == status.HTTP_200_OK, response.data
        return response.data

    def authenticate(self, email="user@example.com", password="SecurePass123!", name="Test User"):
        self.register(email=email, password=password, name=name)
        data = self.login(email=email, password=password)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {data['access']}")
        return data


class AuthenticationTests(BaseAPITestCase):
    # ------------------------------------------------------------------ #
    # Registration
    # ------------------------------------------------------------------ #
    def test_register_success(self):
        payload = {
            "name": "Jane Doe",
            "email": "jane@example.com",
            "password": "SecurePass123!",
        }
        response = self.client.post(REGISTER_URL, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["user"]["email"], "jane@example.com")
        self.assertEqual(response.data["user"]["name"], "Jane Doe")
        self.assertNotIn("password", response.data["user"])

    def test_register_hashes_password(self):
        self.register(email="hash@example.com")
        user = User.objects.get(email="hash@example.com")

        self.assertTrue(user.check_password("SecurePass123!"))
        self.assertNotEqual(user.password, "SecurePass123!")
        self.assertTrue(user.password.startswith(("pbkdf2_", "argon2", "bcrypt")))

    def test_register_duplicate_email_rejected(self):
        self.register(email="dupe@example.com")
        response = self.client.post(
            REGISTER_URL,
            {"name": "Other", "email": "dupe@example.com", "password": "SecurePass123!"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_register_duplicate_email_is_case_insensitive(self):
        self.register(email="case@example.com")
        response = self.client.post(
            REGISTER_URL,
            {"name": "Other", "email": "CASE@example.com", "password": "SecurePass123!"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_missing_fields(self):
        response = self.client.post(REGISTER_URL, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        for field in ("name", "email", "password"):
            self.assertIn(field, response.data)

    def test_register_invalid_email(self):
        response = self.client.post(
            REGISTER_URL,
            {"name": "X", "email": "not-an-email", "password": "SecurePass123!"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_register_weak_password_rejected(self):
        response = self.client.post(
            REGISTER_URL,
            {"name": "Weak", "email": "weak@example.com", "password": "123"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)

    # ------------------------------------------------------------------ #
    # Login
    # ------------------------------------------------------------------ #
    def test_login_success_returns_jwt(self):
        self.register(email="login@example.com")
        response = self.client.post(
            LOGIN_URL, {"email": "login@example.com", "password": "SecurePass123!"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertEqual(response.data["user"]["email"], "login@example.com")

    def test_login_invalid_password(self):
        self.register(email="login2@example.com")
        response = self.client.post(
            LOGIN_URL, {"email": "login2@example.com", "password": "WrongPass123!"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_unknown_email(self):
        response = self.client.post(
            LOGIN_URL, {"email": "ghost@example.com", "password": "SecurePass123!"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_missing_fields(self):
        response = self.client.post(LOGIN_URL, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ------------------------------------------------------------------ #
    # JWT behaviour
    # ------------------------------------------------------------------ #
    def test_unauthenticated_request_rejected(self):
        response = self.client.get(PATIENTS_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("detail", response.data)

    def test_access_token_allows_access(self):
        self.authenticate(email="jwt@example.com")
        response = self.client.get(PATIENTS_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_token_rejected(self):
        self.client.credentials(HTTP_AUTHORIZATION="Bearer not-a-real-token")
        response = self.client.get(PATIENTS_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_refresh_returns_new_access_token(self):
        data = self.authenticate(email="refresh@example.com")
        self.client.credentials()
        response = self.client.post(REFRESH_URL, {"refresh": data["refresh"]}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_token_refresh_with_invalid_token(self):
        response = self.client.post(REFRESH_URL, {"refresh": "bogus"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_returns_current_user(self):
        self.authenticate(email="me@example.com")
        response = self.client.get(ME_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "me@example.com")
        self.assertNotIn("password", response.data)
