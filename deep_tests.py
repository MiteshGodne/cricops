"""
Deep diagnostic tests for accounts, venues, players, teams apps.
Run: python manage.py test deep_tests --verbosity=2
Place this file in project root.
"""
import uuid
import random
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.utils import timezone
from datetime import date, timedelta

from accounts.models import User
from venues.models import Venue
from players.models import Player
from teams.models import Team, TournamentSquad
from tournaments.models import Tournament, Regulation
from matches.models import Match, TeamMatch, Innings


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def make_user(email=None, role="TEAMHEAD"):
    if email is None:
        email = f"user_{uuid.uuid4().hex[:8]}@x.com"
    # FIX: Dynamically generate unique 10-digit phone number to prevent unique constraint failures
    unique_phone = str(random.randint(1000000000, 9999999999))
    return User.objects.create_user(
        email=email, password="Pass@1234",
        first_name="A", last_name="B", phone=unique_phone, role=role
    )

def make_team(user=None, name=None, short=None):
    if not user:
        user = make_user()
    name = name or f"Team_{uuid.uuid4().hex[:4]}"
    short = short or name[:4].upper()
    return Team.objects.create(
        team_name=name, short_name=short,
        city="Mumbai", state="MH", team_head=user
    )

def make_regulation(players_per_side=11, user=None):
    if not user:
        user = make_user(role="ORGANIZER")
    return Regulation.objects.create(
        match_format="T20", overs_per_innings=20,
        players_per_side=players_per_side, tournament_format="LEAGUE",
        created_by=user
    )

def make_tournament(reg=None, t_status="ACCEPTING_APPLICATIONS"):
    organizer = make_user(role="ORGANIZER")
    if not reg:
        reg = make_regulation(user=organizer)
    return Tournament.objects.create(
        name=f"Cup_{uuid.uuid4().hex[:4]}", category="OPEN", regulation=reg,
        start_date=date.today(), end_date=date.today() + timedelta(days=10),
        status=t_status,
        application_deadline=timezone.now() + timedelta(days=5),
        created_by=organizer
    )

def make_player(name=None, team=None):
    name = name or f"Player_{uuid.uuid4().hex[:4]}"
    return Player.objects.create(
        full_name=name, date_of_birth="2000-01-01",
        player_role="BATSMAN", current_team=team
    )

def assertOK(test, res, expected=200):
    """Print full response on failure."""
    if res.status_code != expected:
        print(f"\n[FAIL] Expected {expected}, got {res.status_code}")
        print(f"  Response data: {res.data if hasattr(res, 'data') else res.content}")
    test.assertEqual(res.status_code, expected)


# ═════════════════════════════════════════════
# ACCOUNTS — DEEP TESTS
# ═════════════════════════════════════════════

class AccountsDeepTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        # FIX: Changed role to 'ORGANIZER' to pass database check constraint, while maintaining admin flags
        self.admin_user = make_user(email="admin_test@x.com", role="ORGANIZER")
        self.admin_user.is_staff = True
        self.admin_user.is_superuser = True
        self.admin_user.save()

    def test_db_user_password_is_hashed(self):
        u = User.objects.create_user(email="hash@x.com", password="Plain1234")
        self.assertNotEqual(u.password, "Plain1234")
        self.assertTrue(u.password.startswith("pbkdf2") or u.password.startswith("argon") or u.password.startswith("bcrypt"))

    def test_db_email_verification_token_auto_set(self):
        u = User.objects.create_user(email="tok@x.com", password="Pass@1234")
        self.assertIsNotNone(u.email_verification_token)

    def test_db_uuid_is_unique_per_user(self):
        u1 = User.objects.create_user(email="u1@x.com", password="Pass@1234", phone=str(random.randint(1000000000, 9999999999)))
        u2 = User.objects.create_user(email="u2@x.com", password="Pass@1234", phone=str(random.randint(1000000000, 9999999999)))
        self.assertNotEqual(u1.user_id, u2.user_id)

    def test_db_created_at_auto_set(self):
        u = User.objects.create_user(email="ts@x.com", password="Pass@1234")
        self.assertIsNotNone(u.date_joined)

    def test_db_user_count_after_create(self):
        before = User.objects.count()
        User.objects.create_user(email="count@x.com", password="Pass@1234")
        self.assertEqual(User.objects.count(), before + 1)

    def test_db_user_count_unchanged_on_bad_create(self):
        before = User.objects.count()
        try:
            User.objects.create_user(email="", password="Pass@1234")
        except Exception:
            pass
        self.assertEqual(User.objects.count(), before)

    def test_db_role_choices_enforced_at_db(self):
        u = User.objects.create_user(email="role@x.com", password="Pass@1234", role="PENDING")
        self.assertEqual(u.role, "PENDING")

    def test_api_response_has_no_password_field(self):
        payload = {
            "email": "nopwd@x.com", "password": "Pass@1234",
            "first_name": "A", "last_name": "B", "phone": "1234567890"
        }
        res = self.client.post("/api/accounts/users/", payload, format="json")
        assertOK(self, res, 201)
        self.assertNotIn("password", res.data)

    def test_api_user_db_count_increases(self):
        before = User.objects.count()
        payload = {
            "email": "dbcount@x.com", "password": "Pass@1234",
            "first_name": "A", "last_name": "B", "phone": "1234567891"
        }
        res = self.client.post("/api/accounts/users/", payload, format="json")
        assertOK(self, res, 201)
        self.assertEqual(User.objects.count(), before + 1)

    def test_api_created_user_retrievable_from_db(self):
        payload = {
            "email": "retrieve@x.com", "password": "Pass@1234",
            "first_name": "John", "last_name": "Doe", "phone": "1234567892"
        }
        res = self.client.post("/api/accounts/users/", payload, format="json")
        assertOK(self, res, 201)
        user_id = res.data["user_id"]
        u = User.objects.get(user_id=user_id)
        self.assertEqual(u.email, "retrieve@x.com")
        self.assertEqual(u.first_name, "JOHN")

    def test_api_phone_numeric_only_enforced(self):
        for phone in ["abc123", "98+76543", "98 765 43"]:
            payload = {
                "email": f"ph_{uuid.uuid4().hex[:4]}@x.com", "password": "Pass@1234",
                "first_name": "A", "last_name": "B", "phone": phone
            }
            res = self.client.post("/api/accounts/users/", payload, format="json")
            self.assertEqual(res.status_code, 400)

    def test_api_all_roles_accepted(self):
        for role in ["ORGANIZER", "TEAMHEAD", "UMPIRE", "VIEWER"]:
            payload = {
                "email": f"role_{role.lower()}@x.com", "password": "Pass@1234",
                "first_name": "A", "last_name": "B", "phone": str(random.randint(1000000000, 9999999999)), "role": role
            }
            res = self.client.post("/api/accounts/users/", payload, format="json")
            assertOK(self, res, 201)
            self.assertEqual(res.data["role"], "PENDING")

    def test_api_update_user_persists_to_db(self):
        u = make_user(email="upd@x.com")
        self.client.force_authenticate(user=self.admin_user)
        res = self.client.patch(f"/api/accounts/users/{u.user_id}/", {"phone": "1111111111"}, format="json")
        assertOK(self, res, 200)
        u.refresh_from_db()
        self.assertEqual(u.phone, "1111111111")

    def test_api_delete_user_removes_from_db(self):
        u = make_user(email="del@x.com")
        uid = u.user_id
        self.client.force_authenticate(user=self.admin_user)
        res = self.client.delete(f"/api/accounts/users/{uid}/")
        assertOK(self, res, 204)
        self.assertFalse(User.objects.filter(user_id=uid).exists())

    def test_api_jwt_token_contains_user_id(self):
        User.objects.create_user(
            email="jwt@x.com", password="Pass@1234",
            first_name="A", last_name="B", phone="1234567895"
        )
        res = self.client.post("/api/accounts/login/", {
            "email": "jwt@x.com", "password": "Pass@1234"
        }, format="json")
        assertOK(self, res, 200)
        import base64, json
        token = res.data["access"]
        payload = token.split(".")[1]
        payload += "=" * (4 - len(payload) % 4)
        decoded = json.loads(base64.b64decode(payload))
        self.assertIn("user_id", decoded)


# ═════════════════════════════════════════════
# VENUES — DEEP TESTS
# ═════════════════════════════════════════════

class VenuesDeepTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.organizer = make_user(role="ORGANIZER")
        self.client.force_authenticate(user=self.organizer)
        self.payload = {
            "name": "Wankhede", "address_line": "D Rd",
            "city": "Mumbai", "state": "MH", "country": "India",
            "pincode": 400020, "capacity": 33000,
            "gps_latitude": "18.938620", "gps_longitude": "72.825361",
        }

    def test_db_venue_count_after_create(self):
        before = Venue.objects.count()
        Venue.objects.create(created_by=self.organizer, **self.payload)
        self.assertEqual(Venue.objects.count(), before + 1)

    def test_db_venue_retrievable_after_api_create(self):
        res = self.client.post("/api/venues/", self.payload, format="json")
        assertOK(self, res, 201)
        vid = res.data["venue_id"]
        v = Venue.objects.get(venue_id=vid)
        self.assertEqual(v.name, "Wankhede")
        self.assertEqual(v.city, "Mumbai")

    def test_db_venue_update_persists(self):
        v = Venue.objects.create(created_by=self.organizer, **self.payload)
        res = self.client.patch(f"/api/venues/{v.venue_id}/", {"city": "Pune"}, format="json")
        assertOK(self, res, 200)
        v.refresh_from_db()
        self.assertEqual(v.city, "Pune")

    def test_db_venue_delete_removes_record(self):
        v = Venue.objects.create(created_by=self.organizer, **self.payload)
        vid = v.venue_id
        res = self.client.delete(f"/api/venues/{vid}/")
        assertOK(self, res, 204)
        self.assertFalse(Venue.objects.filter(venue_id=vid).exists())

    def test_db_gps_precision(self):
        v = Venue.objects.create(created_by=self.organizer, **self.payload)
        v.refresh_from_db()
        self.assertIsNotNone(v.gps_latitude)
        self.assertIsNotNone(v.gps_longitude)

    def test_api_created_at_is_readonly(self):
        res = self.client.post("/api/venues/", {**self.payload, "created_at": "2000-01-01"}, format="json")
        assertOK(self, res, 201)
        vid = res.data["venue_id"]
        v = Venue.objects.get(venue_id=vid)
        self.assertNotEqual(str(v.created_at.year), "2000")

    def test_api_multiple_venues_list_count(self):
        Venue.objects.create(created_by=self.organizer, **{**self.payload, "name": "Ground A"})
        Venue.objects.create(created_by=self.organizer, **{**self.payload, "name": "Ground B"})
        res = self.client.get("/api/venues/")
        assertOK(self, res, 200)
        self.assertGreaterEqual(len(res.data), 2)

    def test_api_invalid_gps_rejected(self):
        payload = {**self.payload, "gps_latitude": "not_a_number"}
        res = self.client.post("/api/venues/", payload, format="json")
        self.assertEqual(res.status_code, 400)


# ═════════════════════════════════════════════
# PLAYERS — DEEP TESTS
# ═════════════════════════════════════════════

class PlayersDeepTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.team_head = make_user(role="TEAMHEAD")
        self.client.force_authenticate(user=self.team_head)
        self.team = make_team(user=self.team_head)

    def test_db_player_count_after_create(self):
        before = Player.objects.count()
        make_player(team=self.team)
        self.assertEqual(Player.objects.count(), before + 1)

    def test_db_player_retrievable_after_api_create(self):
        payload = {
            "full_name": "Sachin T", "date_of_birth": "1973-04-24",
            "player_role": "BATSMAN", "current_team": str(self.team.team_id)
        }
        res = self.client.post("/api/players/", payload, format="json")
        assertOK(self, res, 201)
        pid = res.data["player_id"]
        p = Player.objects.get(player_id=pid)
        self.assertEqual(p.full_name, "Sachin T")
        self.assertEqual(p.current_team, self.team)

    def test_db_team_fk_set_correctly(self):
        p = make_player(team=self.team)
        p.refresh_from_db()
        self.assertEqual(p.current_team_id, self.team.team_id)

    def test_db_player_update_persists(self):
        p = make_player(team=self.team)
        res = self.client.patch(f"/api/players/{p.player_id}/", {"nationality": "Australian"}, format="json")
        assertOK(self, res, 200)
        p.refresh_from_db()
        self.assertEqual(p.nationality, "Australian")

    def test_db_deactivate_persists(self):
        p = make_player(team=self.team)
        res = self.client.patch(f"/api/players/{p.player_id}/", {"is_active": False}, format="json")
        assertOK(self, res, 200)
        p.refresh_from_db()
        self.assertFalse(p.is_active)

    def test_db_delete_removes_record(self):
        p = make_player(team=self.team)
        pid = p.player_id
        res = self.client.delete(f"/api/players/{pid}/")
        assertOK(self, res, 204)
        self.assertFalse(Player.objects.filter(player_id=pid).exists())

    def test_db_team_deleted_sets_player_team_null(self):
        team = make_team(user=self.team_head)
        p = make_player(team=team)
        team.delete()
        p.refresh_from_db()
        self.assertIsNone(p.current_team)

    def test_api_filter_active_players_only(self):
        make_player(name="Active One", team=self.team)
        p2 = make_player(name="Inactive One", team=self.team)
        p2.is_active = False
        p2.save()
        res = self.client.get("/api/players/?is_active=True")
        assertOK(self, res, 200)
        self.assertTrue(all(p["is_active"] for p in res.data))

    def test_api_all_roles_valid(self):
        for role in ["BATSMAN", "BOWLER", "ALL_ROUNDER", "WICKETKEEPER"]:
            payload = {
                "full_name": f"Player {role}", "date_of_birth": "2000-01-01",
                "player_role": role, "current_team": str(self.team.team_id)
            }
            res = self.client.post("/api/players/", payload, format="json")
            self.assertEqual(res.status_code, 201)

    def test_api_created_at_updated_at_readonly(self):
        p = make_player(team=self.team)
        res = self.client.patch(f"/api/players/{p.player_id}/",
            {"created_at": "2000-01-01", "updated_at": "2000-01-01"}, format="json")
        assertOK(self, res, 200)
        p.refresh_from_db()
        self.assertNotEqual(str(p.created_at.year), "2000")


# ═════════════════════════════════════════════
# TEAMS — DEEP TESTS
# ═════════════════════════════════════════════

class TeamsDeepTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = make_user()
        self.client.force_authenticate(user=self.user)
        self.team = make_team(user=self.user)
        
        self.organizer = make_user(role="ORGANIZER")
        self.regulation = make_regulation(user=self.organizer)
        self.tournament = make_tournament(reg=self.regulation)
        
        self.player = make_player(team=self.team)
        self.player.current_team = self.team
        self.player.save()

    def test_db_team_count_after_create(self):
        before = Team.objects.count()
        self.client.post("/api/teams/teams/", {
            "team_name": "New XI", "short_name": "NXI",
            "city": "Delhi", "state": "DL"
        }, format="json")
        self.assertEqual(Team.objects.count(), before + 1)

    def test_db_team_created_by_set_to_request_user(self):
        res = self.client.post("/api/teams/teams/", {
            "team_name": "My XI", "short_name": "MXI2",
            "city": "Delhi", "state": "DL"
        }, format="json")
        assertOK(self, res, 201)
        t = Team.objects.get(team_id=res.data["team_id"])
        self.assertEqual(t.created_by, self.user)
        self.assertEqual(t.team_head, self.user)

    def test_db_team_update_persists(self):
        res = self.client.patch(f"/api/teams/teams/{self.team.team_id}/", {"city": "Kolkata"}, format="json")
        assertOK(self, res, 200)
        self.team.refresh_from_db()
        self.assertEqual(self.team.city, "Kolkata")

    def test_db_team_delete_removes_record(self):
        tid = self.team.team_id
        res = self.client.delete(f"/api/teams/teams/{tid}/")
        assertOK(self, res, 204)
        self.assertFalse(Team.objects.filter(team_id=tid).exists())

    def test_db_squad_count_after_add(self):
        before = TournamentSquad.objects.count()
        TournamentSquad.objects.create(
            tournament=self.tournament, team=self.team,
            player=self.player, jersey_number=7
        )
        self.assertEqual(TournamentSquad.objects.count(), before + 1)

    def test_db_squad_entry_retrievable(self):
        sq = TournamentSquad.objects.create(
            tournament=self.tournament, team=self.team,
            player=self.player, jersey_number=7
        )
        sq.refresh_from_db()
        self.assertEqual(sq.player, self.player)
        self.assertEqual(sq.team, self.team)
        self.assertEqual(sq.tournament, self.tournament)

    def test_db_squad_api_create_persists(self):
        before = TournamentSquad.objects.count()
        res = self.client.post("/api/teams/squads/", {
            "tournament": str(self.tournament.tournament_id),
            "team": str(self.team.team_id),
            "player": str(self.player.player_id),
            "jersey_number": 99,
        }, format="json")
        assertOK(self, res, 201)
        self.assertEqual(TournamentSquad.objects.count(), before + 1)

    def test_db_squad_deleted_when_team_deleted(self):
        TournamentSquad.objects.create(
            tournament=self.tournament, team=self.team,
            player=self.player, jersey_number=7
        )
        tid = self.team.team_id
        self.team.delete()
        self.assertFalse(TournamentSquad.objects.filter(team_id=tid).exists())

    def test_api_squad_response_has_correct_fields(self):
        res = self.client.post("/api/teams/squads/", {
            "tournament": str(self.tournament.tournament_id),
            "team": str(self.team.team_id),
            "player": str(self.player.player_id),
            "jersey_number": 11,
        }, format="json")
        assertOK(self, res, 201)
        for field in ["squad_id", "tournament", "team", "player", "jersey_number", "squad_role"]:
            self.assertIn(field, res.data)

    def test_api_squad_role_choices(self):
        players = [make_player(team=self.team) for _ in range(3)]
        for p in players:
            p.current_team = self.team
            p.save()
        for i, role in enumerate(["PLAYER", "CAPTAIN", "VICE_CAPTAIN"]):
            res = self.client.post("/api/teams/squads/", {
                "tournament": str(self.tournament.tournament_id),
                "team": str(self.team.team_id),
                "player": str(players[i].player_id),
                "jersey_number": i + 1,
                "squad_role": role,
            }, format="json")
            self.assertEqual(res.status_code, 201)
            self.assertEqual(res.data["squad_role"], role)

    def test_api_nonexistent_team_returns_404(self):
        fake_id = "00000000-0000-0000-0000-000000000000"
        res = self.client.get(f"/api/teams/teams/{fake_id}/")
        self.assertEqual(res.status_code, 404)
        
        


def make_user(email=None, role="ORGANIZER"):
    if email is None:
        email = f"user_{uuid.uuid4().hex[:8]}@x.com"
    unique_phone = str(random.randint(1000000000, 9999999999))
    return User.objects.create_user(
        email=email, password="Pass@1234",
        first_name="A", last_name="B", phone=unique_phone, role=role
    )

def make_team(name=None, short=None, user=None):
    if not user:
        user = make_user(role="TEAMHEAD")
    name = name or f"Team_{uuid.uuid4().hex[:4]}"
    short = short or name[:4].upper()
    return Team.objects.create(team_name=name, short_name=short, city="Mumbai", state="MH", team_head=user)

def make_regulation(players_per_side=2, overs=2, user=None):
    if not user:
        user = make_user(role="ORGANIZER")
    return Regulation.objects.create(
        match_format="T20", overs_per_innings=overs,
        players_per_side=players_per_side, tournament_format="LEAGUE",
        created_by=user
    )

def make_tournament(reg=None, user=None):
    if not user:
        user = make_user(role="ORGANIZER")
    if not reg:
        reg = make_regulation(user=user)
    return Tournament.objects.create(
        name=f"Cup_{uuid.uuid4().hex[:4]}", category="OPEN", regulation=reg,
        start_date=date.today(), end_date=date.today() + timedelta(days=5),
        status="ONGOING", created_by=user
    )

def make_venue():
    return Venue.objects.create(name="Ground", address_line="Rd", city="Mumbai")

def make_match(tournament=None, venue=None, umpire=None):
    if not tournament:
        tournament = make_tournament()
    if not venue:
        venue = make_venue()
    return Match.objects.create(
        tournament=tournament, venue=venue, innings_count=2, primary_umpire=umpire
    )

def make_squad_player(team, tournament, jersey=1, name=None):
    p = Player.objects.create(
        full_name=name or f"P_{uuid.uuid4().hex[:4]}", date_of_birth="2000-01-01",
        player_role="BATSMAN", current_team=team
    )
    TournamentSquad.objects.create(tournament=tournament, team=team, player=p, jersey_number=jersey, is_playing_xi=True)
    return p

def assertOK(test, res, expected):
    test.assertEqual(res.status_code, expected)


# ═════════════════════════════════════════════
# PERMISSION & MATRIX AUTOMATION TESTS
# ═════════════════════════════════════════════

class DeepSystemArchitectureTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.organizer = make_user(role="ORGANIZER")
        self.team_head = make_user(role="TEAMHEAD")
        self.umpire = make_user(role="UMPIRE")

        self.reg = make_regulation(players_per_side=2, overs=1, user=self.organizer)
        self.tournament = make_tournament(reg=self.reg, user=self.organizer)
        self.match = make_match(tournament=self.tournament, umpire=self.umpire)
        
        self.teamA = make_team(user=self.team_head)
        self.teamB = make_team()

        # FIX: Added unique registered_name and registered_short_name to clear the database unique constraint constraints
        from tournaments.models import Application
        Application.objects.create(
            team=self.teamA, tournament=self.tournament, status="ACCEPTED",
            registered_name="Alpha Team", registered_short_name="ATH"
        )
        Application.objects.create(
            team=self.teamB, tournament=self.tournament, status="ACCEPTED",
            registered_name="Beta Team", registered_short_name="BTM"
        )

        self.a1 = make_squad_player(self.teamA, self.tournament, jersey=1)
        self.a2 = make_squad_player(self.teamA, self.tournament, jersey=2)
        self.b1 = make_squad_player(self.teamB, self.tournament, jersey=1)
        self.b2 = make_squad_player(self.teamB, self.tournament, jersey=2)

        TeamMatch.objects.create(match=self.match, team=self.teamA, side="A")
        TeamMatch.objects.create(match=self.match, team=self.teamB, side="B")

    def test_matrix_right_task_wrong_permission_blocks(self):
        """Matrix: Submitting toss requires the Tournament Creator Organizer, not an Umpire"""
        self.client.force_authenticate(user=self.umpire)
        payload = {"match_id": str(self.match.match_id), "toss_winner_team_id": str(self.teamA.team_id), "toss_decision": "BAT"}
        res = self.client.post("/api/matches/team-matches/submit-toss/", payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_matrix_wrong_task_right_permission_bounds(self):
        """Matrix: Organizer can hit toss, but it fails if teams mapping configuration is invalid"""
        extra_match = make_match(tournament=self.tournament) # No teams linked
        self.client.force_authenticate(user=self.organizer)
        payload = {"match_id": str(extra_match.match_id), "toss_winner_team_id": str(self.teamA.team_id), "toss_decision": "BAT"}
        res = self.client.post("/api/matches/team-matches/submit-toss/", payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_automation_e2e_scoring_and_standings_sync(self):
        """Validates the live automation cycle from Toss -> Ball Scoring -> Standings Calculation"""
        self.client.force_authenticate(user=self.organizer)
        res_toss = self.client.post("/api/matches/team-matches/submit-toss/", {
            "match_id": str(self.match.match_id), "toss_winner_team_id": str(self.teamA.team_id), "toss_decision": "BAT"
        }, format="json")
        self.assertEqual(res_toss.status_code, status.HTTP_200_OK)
        innings_1_id = res_toss.data["innings_id"]

        # Instantiate standing records
        TournamentStanding.objects.get_or_create(tournament=self.tournament, team=self.teamA)
        TournamentStanding.objects.get_or_create(tournament=self.tournament, team=self.teamB)

        # Log active delivery as the assigned umpire
        self.client.force_authenticate(user=self.umpire)
        payload = {
            "innings_id": innings_1_id, "striker_id": str(self.a1.player_id),
            "non_striker_id": str(self.a2.player_id), "bowler_id": str(self.b1.player_id),
            "runs_scored": 0, "wicket_type": "BOWLED"
        }
        res_delivery = self.client.post("/api/matches/deliveries/submit/", payload, format="json")
        self.assertEqual(res_delivery.status_code, status.HTTP_201_CREATED)

        # Assert automated target rollover generation and innings calculation metrics
        self.match.refresh_from_db()
        self.assertTrue(Innings.objects.filter(match=self.match, innings_number=2).exists())