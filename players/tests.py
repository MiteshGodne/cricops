from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from players.models import Player
from accounts.models import User
from teams.models import Team


def make_team():
    user = User.objects.create_user(
        email="head@team.com", password="Pass@1234",
        first_name="A", last_name="B", phone="9999999999"
    )
    return Team.objects.create(
        team_name="Test XI", short_name="TXI",
        city="Mumbai", state="MH", team_head=user
    )

def make_player(**kwargs):
    defaults = dict(
        full_name="Virat Kohli",
        date_of_birth="1988-11-05",
        player_role="BATSMAN",
        nationality="Indian",
    )
    defaults.update(kwargs)
    return Player.objects.create(**defaults)


# ─────────────────────────────────────────────
# MODEL TESTS
# ─────────────────────────────────────────────

class PlayerModelTest(TestCase):

    def test_create_player_no_team(self):
        p = make_player()
        self.assertEqual(p.full_name, "Virat Kohli")
        self.assertIsNone(p.current_team)
        self.assertTrue(p.is_active)

    def test_create_player_with_team(self):
        team = make_team()
        p = make_player(full_name="Rohit Sharma", current_team=team)
        self.assertEqual(p.current_team, team)

    def test_uuid_primary_key(self):
        p = make_player()
        self.assertIsNotNone(p.player_id)

    def test_player_str(self):
        p = make_player()
        self.assertIn("Virat Kohli", str(p))
        self.assertIn("BATSMAN", str(p))

    def test_player_roles(self):
        for role in ["BATSMAN", "BOWLER", "ALL_ROUNDER", "WICKETKEEPER"]:
            p = make_player(full_name=f"Player {role}", player_role=role)
            self.assertEqual(p.player_role, role)

    def test_team_deleted_sets_null(self):
        team = make_team()
        p = make_player(current_team=team)
        team.delete()
        p.refresh_from_db()
        self.assertIsNone(p.current_team)

    def test_ordering_by_name(self):
        make_player(full_name="Zaheer Khan", player_role="BOWLER")
        make_player(full_name="Anil Kumble", player_role="BOWLER")
        players = list(Player.objects.all())
        names = [p.full_name for p in players]
        self.assertEqual(names, sorted(names))

    def test_is_active_default_true(self):
        p = make_player()
        self.assertTrue(p.is_active)

    def test_optional_fields(self):
        p = Player.objects.create(
            full_name="Unknown", date_of_birth="2000-01-01", player_role="BOWLER"
        )
        self.assertEqual(p.nationality, "")
        self.assertFalse(bool(p.identity_document))


# ─────────────────────────────────────────────
# API TESTS
# ─────────────────────────────────────────────

class PlayerAPITest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.team = make_team()
        self.valid_payload = {
            "full_name": "MS Dhoni",
            "date_of_birth": "1981-07-07",
            "player_role": "WICKETKEEPER",
            "nationality": "Indian",
            "current_team": str(self.team.team_id),
        }

    def test_create_player(self):
        res = self.client.post("/api/players/", self.valid_payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["full_name"], "MS Dhoni")
        self.assertIn("player_id", res.data)

    def test_create_player_no_team(self):
        payload = {**self.valid_payload, "current_team": None, "full_name": "No Team"}
        res = self.client.post("/api/players/", payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIsNone(res.data["current_team"])

    def test_create_player_missing_required(self):
        res = self.client.post("/api/players/", {"full_name": "Incomplete"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_player_invalid_role(self):
        payload = {**self.valid_payload, "player_role": "GOALKEEPER"}
        res = self.client.post("/api/players/", payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_players(self):
        make_player()
        res = self.client.get("/api/players/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(res.data), 1)

    def test_retrieve_player(self):
        p = make_player()
        res = self.client.get(f"/api/players/{p.player_id}/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["full_name"], "Virat Kohli")

    def test_update_player(self):
        p = make_player()
        res = self.client.patch(f"/api/players/{p.player_id}/", {"nationality": "Indian"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["nationality"], "Indian")

    def test_deactivate_player(self):
        p = make_player()
        res = self.client.patch(f"/api/players/{p.player_id}/", {"is_active": False}, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertFalse(res.data["is_active"])

    def test_delete_player(self):
        p = make_player()
        res = self.client.delete(f"/api/players/{p.player_id}/")
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Player.objects.filter(player_id=p.player_id).exists())

    def test_filter_by_current_team(self):
        make_player(full_name="With Team", current_team=self.team)
        make_player(full_name="No Team")
        res = self.client.get(f"/api/players/?current_team={self.team.team_id}")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["full_name"], "With Team")

    def test_filter_by_is_active(self):
        make_player(full_name="Active Player", is_active=True)
        make_player(full_name="Inactive Player", is_active=False)
        res = self.client.get("/api/players/?is_active=True")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(all(p["is_active"] for p in res.data))

    def test_read_only_fields(self):
        p = make_player()
        fake_id = "00000000-0000-0000-0000-000000000000"
        res = self.client.patch(f"/api/players/{p.player_id}/", {"player_id": fake_id}, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertNotEqual(res.data["player_id"], fake_id)  # read_only, ignored

    def test_invalid_team_id(self):
        payload = {**self.valid_payload, "current_team": "00000000-0000-0000-0000-000000000000"}
        res = self.client.post("/api/players/", payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)