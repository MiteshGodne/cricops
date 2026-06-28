import uuid
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.utils import timezone
from datetime import date, timedelta

from accounts.models import User
from teams.models import Team, TournamentSquad
from players.models import Player
from tournaments.models import Tournament, Regulation, Application


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def make_user(email=None, role="TEAMHEAD"):
    if email is None:
        email = f"user_{uuid.uuid4().hex[:8]}@x.com"
    return User.objects.create_user(
        email=email, password="Pass@1234",
        first_name="A", last_name="B", phone="9999999999", role=role
    )

def make_team(user=None, name="Mumbai XI", short="MXI"):
    if not user:
        user = make_user()
    return Team.objects.create(
        team_name=name, short_name=short,
        city="Mumbai", state="MH", team_head=user
    )

def make_regulation(players_per_side=11):
    return Regulation.objects.create(
        match_format="T20", overs_per_innings=20,
        players_per_side=players_per_side, tournament_format="LEAGUE"
    )

def make_tournament(reg=None, status="ACCEPTING_APPLICATIONS"):
    if not reg:
        reg = make_regulation()
    organizer = make_user(role="ORGANIZER")
    return Tournament.objects.create(
        name="Test Cup", category="OPEN", regulation=reg,
        start_date=date.today(), end_date=date.today() + timedelta(days=10),
        status=status,
        application_deadline=timezone.now() + timedelta(days=5),
        created_by=organizer
    )

def make_player(name="Player One", team=None):
    p = Player.objects.create(
        full_name=name, date_of_birth="2000-01-01",
        player_role="BATSMAN", current_team=team
    )
    return p


# ─────────────────────────────────────────────
# TEAM MODEL TESTS
# ─────────────────────────────────────────────

class TeamModelTest(TestCase):

    def test_create_team(self):
        t = make_team()
        self.assertEqual(t.team_name, "Mumbai XI")
        self.assertTrue(t.is_active)

    def test_uuid_pk(self):
        t = make_team()
        self.assertIsNotNone(t.team_id)

    def test_str(self):
        t = make_team()
        self.assertIn("Mumbai XI", str(t))
        self.assertIn("MXI", str(t))

    def test_ordering_by_name(self):
        u = make_user()
        Team.objects.create(team_name="Zebra XI", short_name="ZXI", city="X", state="Y", team_head=u)
        Team.objects.create(team_name="Alpha XI", short_name="AXI", city="X", state="Y", team_head=u)
        names = list(Team.objects.values_list("team_name", flat=True))
        self.assertEqual(names, sorted(names))

    def test_team_head_null_on_user_delete(self):
        u = make_user()
        t = Team.objects.create(team_name="Del Team", short_name="DT", city="X", state="Y", team_head=u)
        u.delete()
        t.refresh_from_db()
        self.assertIsNone(t.team_head)


# ─────────────────────────────────────────────
# TEAM API TESTS
# ─────────────────────────────────────────────

class TeamAPITest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = make_user()
        self.client.force_authenticate(user=self.user)
        self.payload = {
            "team_name": "Chennai XI",
            "short_name": "CXI",
            "city": "Chennai",
            "state": "TN",
        }

    def test_create_team(self):
        res = self.client.post("/api/teams/teams/", self.payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["team_name"], "Chennai XI")
        self.assertEqual(str(res.data["team_head"]), str(self.user.user_id))
        self.assertEqual(str(res.data["created_by"]), str(self.user.user_id))

    def test_create_team_missing_name(self):
        payload = {**self.payload, "team_name": ""}
        res = self.client.post("/api/teams/teams/", payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_team_missing_short_name(self):
        payload = {**self.payload, "short_name": ""}
        res = self.client.post("/api/teams/teams/", payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_teams(self):
        make_team()
        res = self.client.get("/api/teams/teams/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(res.data), 1)

    def test_retrieve_team(self):
        t = make_team(user=self.user)
        res = self.client.get(f"/api/teams/teams/{t.team_id}/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["team_name"], "Mumbai XI")

    def test_update_team(self):
        t = make_team(user=self.user)
        res = self.client.patch(f"/api/teams/teams/{t.team_id}/", {"city": "Pune"}, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["city"], "Pune")

    def test_delete_team(self):
        t = make_team(user=self.user)
        res = self.client.delete(f"/api/teams/teams/{t.team_id}/")
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_read_only_fields_ignored(self):
        t = make_team(user=self.user)
        fake_id = "00000000-0000-0000-0000-000000000000"
        res = self.client.patch(f"/api/teams/teams/{t.team_id}/", {"team_id": fake_id}, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertNotEqual(res.data["team_id"], fake_id)


# ─────────────────────────────────────────────
# TOURNAMENT SQUAD MODEL TESTS
# ─────────────────────────────────────────────

class TournamentSquadModelTest(TestCase):

    def setUp(self):
        self.team = make_team()
        self.tournament = make_tournament()
        self.player = make_player(team=self.team)

    def test_create_squad_entry(self):
        sq = TournamentSquad.objects.create(
            tournament=self.tournament, team=self.team,
            player=self.player, jersey_number=18,
        )
        self.assertEqual(sq.squad_role, "PLAYER")
        self.assertTrue(sq.is_playing_xi)

    def test_unique_player_per_tournament(self):
        TournamentSquad.objects.create(
            tournament=self.tournament, team=self.team,
            player=self.player, jersey_number=18
        )
        team2 = make_team(make_user(), name="Delhi XI", short="DXI")
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            TournamentSquad.objects.create(
                tournament=self.tournament, team=team2,
                player=self.player, jersey_number=7
            )

    def test_unique_jersey_per_team_per_tournament(self):
        TournamentSquad.objects.create(
            tournament=self.tournament, team=self.team,
            player=self.player, jersey_number=18
        )
        p2 = make_player(name="Player Two", team=self.team)
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            TournamentSquad.objects.create(
                tournament=self.tournament, team=self.team,
                player=p2, jersey_number=18
            )

    def test_str(self):
        sq = TournamentSquad.objects.create(
            tournament=self.tournament, team=self.team,
            player=self.player, jersey_number=18
        )
        self.assertIn(self.player.full_name, str(sq))


# ─────────────────────────────────────────────
# TOURNAMENT SQUAD API TESTS
# ─────────────────────────────────────────────

class TournamentSquadAPITest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = make_user()
        self.client.force_authenticate(user=self.user)
        self.team = make_team(user=self.user)
        self.tournament = make_tournament()
        self.player = make_player(name="Sachin T", team=self.team)
        self.player.current_team = self.team
        self.player.save()
        self.payload = {
            "tournament": str(self.tournament.tournament_id),
            "team": str(self.team.team_id),
            "player": str(self.player.player_id),
            "jersey_number": 10,
            "squad_role": "PLAYER",
            "is_playing_xi": True,
        }

    def test_add_player_to_squad(self):
        res = self.client.post("/api/teams/squads/", self.payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["jersey_number"], 10)

    def test_player_not_in_team_rejected(self):
        other_team = make_team(make_user(), name="Other XI", short="OXI")
        payload = {**self.payload, "team": str(other_team.team_id)}
        res = self.client.post("/api/teams/squads/", payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", res.data)

    def test_tournament_not_accepting_rejected(self):
        closed_t = make_tournament(status="APPLICATIONS_CLOSED")
        payload = {**self.payload, "tournament": str(closed_t.tournament_id)}
        res = self.client.post("/api/teams/squads/", payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", res.data)

    def test_duplicate_player_rejected(self):
        res1 = self.client.post("/api/teams/squads/", self.payload, format="json")
        self.assertEqual(res1.status_code, status.HTTP_201_CREATED)
        payload2 = {**self.payload, "jersey_number": 99}
        res = self.client.post("/api/teams/squads/", payload2, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("unique", str(res.data).lower())

    def test_duplicate_jersey_rejected(self):
        p2 = make_player(name="Player Two", team=self.team)
        p2.current_team = self.team
        p2.save()
        res1 = self.client.post("/api/teams/squads/", self.payload, format="json")
        self.assertEqual(res1.status_code, status.HTTP_201_CREATED)
        payload2 = {**self.payload, "player": str(p2.player_id), "jersey_number": 10}
        res = self.client.post("/api/teams/squads/", payload2, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("unique", str(res.data).lower())

    def test_playing_xi_limit(self):
        reg = make_regulation(players_per_side=2)
        t = make_tournament(reg=reg)
        players = []
        for i in range(3):
            p = make_player(name=f"P{i}", team=self.team)
            p.current_team = self.team
            p.save()
            players.append(p)

        for i, p in enumerate(players[:2]):
            self.client.post("/api/teams/squads/", {
                **self.payload,
                "tournament": str(t.tournament_id),
                "player": str(p.player_id),
                "jersey_number": i + 1,
            }, format="json")

        res = self.client.post("/api/teams/squads/", {
            **self.payload,
            "tournament": str(t.tournament_id),
            "player": str(players[2].player_id),
            "jersey_number": 3,
        }, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Playing XI limit", res.data["error"])

    def test_list_squads(self):
        TournamentSquad.objects.create(
            tournament=self.tournament, team=self.team,
            player=self.player, jersey_number=10
        )
        res = self.client.get("/api/teams/squads/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(res.data), 1)