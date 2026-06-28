from django.test import TestCase
from django.core.exceptions import ValidationError
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import User
from venues.models import Venue

# ─────────────────────────────────────────────
# VENUES
# ─────────────────────────────────────────────

class VenueModelTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.valid_payload = {
            "name": "Wankhede Stadium",
            "address_line": "D Rd, Churchgate",
            "city": "Mumbai",
            "state": "Maharashtra",
            "country": "India",
            "pincode": 400020,
            "capacity": 33000,
            "gps_latitude": "18.938620",
            "gps_longitude": "72.825361",
        }

    # Model-level tests
    def test_create_venue_success(self):
        v = Venue.objects.create(**self.valid_payload)
        self.assertEqual(v.name, "Wankhede Stadium")
        self.assertTrue(v.is_active)

    def test_venue_str(self):
        v = Venue.objects.create(**self.valid_payload)
        self.assertIn("Wankhede Stadium", str(v))
        self.assertIn("Mumbai", str(v))

    def test_venue_uuid_pk(self):
        v = Venue.objects.create(**self.valid_payload)
        self.assertIsNotNone(v.venue_id)

    def test_venue_optional_fields(self):
        v = Venue.objects.create(
            name="Local Ground", address_line="Main Rd", city="Bhopal"
        )
        self.assertIsNone(v.capacity)
        self.assertIsNone(v.gps_latitude)

    # API tests
    def test_api_create_venue(self):
        res = self.client.post("/api/venues/", self.valid_payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["name"], "Wankhede Stadium")
        self.assertIn("venue_id", res.data)

    def test_api_create_venue_missing_required(self):
        payload = {"name": "No Address"}  # missing address_line & city
        res = self.client.post("/api/venues/", payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_api_list_venues(self):
        Venue.objects.create(**self.valid_payload)
        res = self.client.get("/api/venues/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(res.data), 1)

    def test_api_retrieve_venue(self):
        v = Venue.objects.create(**self.valid_payload)
        res = self.client.get(f"/api/venues/{v.venue_id}/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["city"], "Mumbai")

    def test_api_update_venue(self):
        v = Venue.objects.create(**self.valid_payload)
        res = self.client.patch(f"/api/venues/{v.venue_id}/", {"city": "Pune"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["city"], "Pune")

    def test_api_delete_venue(self):
        v = Venue.objects.create(**self.valid_payload)
        res = self.client.delete(f"/api/venues/{v.venue_id}/")
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Venue.objects.filter(venue_id=v.venue_id).exists())

    def test_api_venue_ordering_by_name(self):
        Venue.objects.create(name="Zeta Ground", address_line="Z", city="Delhi")
        Venue.objects.create(name="Alpha Ground", address_line="A", city="Delhi")
        res = self.client.get("/api/venues/")
        data = res.data.get("results", res.data) if isinstance(res.data, dict) else res.data
        names = [v["name"] for v in data]
        self.assertEqual(names, sorted(names))