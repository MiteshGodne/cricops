from django.test import TestCase
from django.core.exceptions import ValidationError
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import User
from venues.models import Venue


# ─────────────────────────────────────────────
# ACCOUNTS
# ─────────────────────────────────────────────

class UserModelTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.valid_payload = {
            "email": "test@example.com",
            "password": "Test@1234",
            "first_name": "john",
            "middle_name": "doe",
            "last_name": "smith",
            "phone": "9876543210",
            "role": "PENDING"
        }

    # Model-level tests
    def test_create_user_success(self):
        user = User.objects.create_user(**self.valid_payload)
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.first_name, "john") 
        self.assertFalse(user.is_email_verified)
        self.assertFalse(user.is_phone_verified)

    def test_email_is_unique(self):
        User.objects.create_user(**self.valid_payload)
        with self.assertRaises(Exception):
            User.objects.create_user(**self.valid_payload)

    def test_create_superuser(self):
        su = User.objects.create_superuser(email="admin@example.com", password="Admin@1234")
        self.assertTrue(su.is_staff)
        self.assertTrue(su.is_superuser)

    def test_create_user_without_email_raises(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(email="", password="Test@1234")

    def test_create_user_without_password_raises(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(email="x@x.com", password="")

    def test_user_role_default(self):
        user = User.objects.create_user(email="viewer@x.com", password="Test@1234")
        self.assertEqual(user.role, "PENDING")

    def test_uuid_primary_key(self):
        user = User.objects.create_user(**self.valid_payload)
        self.assertIsNotNone(user.user_id)

    # API tests
    def test_api_register_user(self):
        res = self.client.post("/api/accounts/users/", self.valid_payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["email"], "test@example.com")
        self.assertEqual(res.data["first_name"], "JOHN")     
        self.assertEqual(res.data["last_name"], "SMITH")
        self.assertNotIn("password", res.data)             

    def test_api_register_missing_email(self):
        payload = {**self.valid_payload, "email": ""}
        res = self.client.post("/api/accounts/users/", payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", res.data)

    def test_api_register_missing_first_name(self):
        payload = {**self.valid_payload, "first_name": ""}
        res = self.client.post("/api/accounts/users/", payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_api_register_non_numeric_phone(self):
        payload = {**self.valid_payload, "phone": "98abc43210"}
        res = self.client.post("/api/accounts/users/", payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("phone", res.data)

    # def test_api_register_invalid_role(self):
    #     payload = {**self.valid_payload, "role": "BATMAN"}
    #     res = self.client.post("/api/accounts/users/", payload, format="json")
    #     self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_api_duplicate_email(self):
        self.client.post("/api/accounts/users/", self.valid_payload, format="json")
        res = self.client.post("/api/accounts/users/", self.valid_payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_api_login_success(self):
        User.objects.create_user(**self.valid_payload)
        res = self.client.post("/api/accounts/login/", {
            "email": "test@example.com",
            "password": "Test@1234"
        }, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("access", res.data)
        self.assertIn("refresh", res.data)

    def test_api_login_wrong_password(self):
        User.objects.create_user(**self.valid_payload)
        res = self.client.post("/api/accounts/login/", {
            "email": "test@example.com",
            "password": "WrongPass"
        }, format="json")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_api_middle_name_uppercase(self):
        res = self.client.post("/api/accounts/users/", self.valid_payload, format="json")
        self.assertEqual(res.data["middle_name"], "DOE")

    def test_api_middle_name_optional(self):
        payload = {**self.valid_payload, "email": "nomiddle@x.com"}
        payload.pop("middle_name", None)
        res = self.client.post("/api/accounts/users/", payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)


# --- accounts/tests.py additions ---
class ApprovalFlowTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser(email="admin2@x.com", password="Admin@1234")
        self.client.force_authenticate(user=self.admin)

    def make_pending(self, apply_for):
        return User.objects.create_user(
            email=f"{apply_for.lower()}@x.com", password="Pass@1234",
            first_name="A", last_name="B", phone="9990001111",
            apply_for=apply_for, role="PENDING"
        )

    def test_approve_organizer_success(self):
        u = self.make_pending("ORGANIZER")
        res = self.client.post(f"/api/accounts/users/{u.user_id}/approve-organizer/", {}, format="json")
        self.assertEqual(res.status_code, 200)
        u.refresh_from_db()
        self.assertEqual(u.role, "ORGANIZER")

    def test_approve_organizer_wrong_apply_for_rejected(self):
        u = self.make_pending("UMPIRE")
        res = self.client.post(f"/api/accounts/users/{u.user_id}/approve-organizer/", {}, format="json")
        self.assertEqual(res.status_code, 400)

    def test_reject_pending_user(self):
        u = self.make_pending("ORGANIZER")
        res = self.client.post(f"/api/accounts/users/{u.user_id}/reject/", {}, format="json")
        self.assertEqual(res.status_code, 200)
        u.refresh_from_db()
        self.assertEqual(u.role, "REJECTED")

    def test_non_admin_cannot_approve(self):
        normal = User.objects.create_user(email="n@x.com", password="Pass@1234",
            first_name="A", last_name="B", phone="2223334444")
        self.client.force_authenticate(user=normal)
        u = self.make_pending("ORGANIZER")
        res = self.client.post(f"/api/accounts/users/{u.user_id}/approve-organizer/", {}, format="json")
        self.assertEqual(res.status_code, 403)

    def test_pending_user_blocked_from_organizer_actions(self):
        u = self.make_pending("ORGANIZER")
        self.client.force_authenticate(user=u)
        res = self.client.post("/api/tournaments/regulations/", {
            "match_format": "T20", "overs_per_innings": 20,
            "players_per_side": 11, "tournament_format": "LEAGUE",
        }, format="json")
        self.assertEqual(res.status_code, 403)  # still PENDING, IsOrganizer blocks