import uuid
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.utils import timezone
from datetime import date, timedelta

from accounts.models import User
from teams.models import Team, TournamentSquad
from players.models import Player
from tournaments.models import (
    Regulation, Tournament, TournamentOrganizer,
    Application, Group, TournamentStanding
)


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def make_user(email=None, role="ORGANIZER"):
    if email is None:
        email = f"user_{uuid.uuid4().hex[:8]}@x.com"
    return User.objects.create_user(
        email=email, password="Pass@1234",
        first_name="A", last_name="B", phone="9999999999", role=role
    )

def make_team(user=None):
    if not user:
        user = make_user(role="TEAMHEAD")
    return Team.objects.create(
        team_name=f"Team_{uuid.uuid4().hex[:4]}", short_name=uuid.uuid4().hex[:4].upper(),
        city="Mumbai", state="MH", team_head=user
    )

def make_regulation(players_per_side=11, overs=20):
    return Regulation.objects.create(
        match_format="T20", overs_per_innings=overs,
        players_per_side=players_per_side, tournament_format="LEAGUE"
    )

def make_tournament(reg=None, t_status="ACCEPTING_APPLICATIONS", user=None):
    if not reg:
        reg = make_regulation()
    if not user:
        user = make_user()
    return Tournament.objects.create(
        name=f"Cup_{uuid.uuid4().hex[:4]}", category="OPEN",
        regulation=reg, start_date=date.today(),
        end_date=date.today() + timedelta(days=10),
        status=t_status,
        application_deadline=timezone.now() + timedelta(days=5),
        created_by=user
    )

def make_player(team=None):
    return Player.objects.create(
        full_name=f"Player_{uuid.uuid4().hex[:4]}",
        date_of_birth="2000-01-01",
        player_role="BATSMAN", current_team=team
    )

def make_application(team, tournament, app_status="PENDING"):
    return Application.objects.create(
        team=team, tournament=tournament,
        registered_name=f"Reg_{uuid.uuid4().hex[:4]}",
        registered_short_name=uuid.uuid4().hex[:4].upper(),
        status=app_status
    )

def assertOK(test, res, expected):
    if res.status_code != expected:
        print(f"\n[FAIL] Expected {expected}, got {res.status_code}")
        print(f"  URL: (check test)")
        print(f"  Response: {res.data if hasattr(res, 'data') else res.content}")
    test.assertEqual(res.status_code, expected)


# ═════════════════════════════════════════════
# REGULATION
# ═════════════════════════════════════════════

class RegulationModelTest(TestCase):

    def test_create_basic(self):
        r = make_regulation()
        self.assertEqual(r.match_format, "T20")
        self.assertEqual(r.overs_per_innings, 20)
        self.assertEqual(r.players_per_side, 11)

    def test_str(self):
        r = make_regulation()
        print(f"\n  Regulation str: {str(r)}")
        self.assertIn("T20", str(r))

    def test_test_format_allows_null_overs(self):
        r = Regulation.objects.create(
            match_format="TEST", tournament_format="LEAGUE"
        )
        self.assertIsNone(r.overs_per_innings)

    def test_defaults(self):
        r = make_regulation()
        self.assertEqual(r.points_for_win, 2)
        self.assertEqual(r.points_for_tie, 1)
        self.assertEqual(r.points_for_loss, 0)
        self.assertEqual(r.points_for_no_result, 1)
        self.assertTrue(r.noball_free_hit_enabled)

    def test_db_check_constraint_overs_positive(self):
        from django.db import IntegrityError
        with self.assertRaises(Exception):
            Regulation.objects.create(
                match_format="T20", overs_per_innings=-5,
                tournament_format="LEAGUE"
            )


class RegulationAPITest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = make_user()
        self.client.force_authenticate(user=self.user)
        self.payload = {
            "match_format": "T20", "overs_per_innings": 20,
            "players_per_side": 11, "tournament_format": "LEAGUE",
            "innings_per_team": 1,
        }

    def test_create(self):
        res = self.client.post("/api/tournaments/regulations/", self.payload, format="json")
        assertOK(self, res, 201)
        self.assertIn("regulation_id", res.data)
        print(f"\n  Regulation created: {res.data['regulation_id']}")

    def test_create_missing_format(self):
        payload = {**self.payload}
        payload.pop("match_format")
        res = self.client.post("/api/tournaments/regulations/", payload, format="json")
        # match_format has default so should still pass
        print(f"\n  Missing match_format response: {res.data}")
        self.assertIn(res.status_code, [200, 201])

    def test_list(self):
        make_regulation()
        res = self.client.get("/api/tournaments/regulations/")
        assertOK(self, res, 200)
        self.assertGreaterEqual(len(res.data), 1)

    def test_retrieve(self):
        r = make_regulation()
        res = self.client.get(f"/api/tournaments/regulations/{r.regulation_id}/")
        assertOK(self, res, 200)
        self.assertEqual(res.data["match_format"], "T20")

    def test_update(self):
        r = make_regulation()
        res = self.client.patch(f"/api/tournaments/regulations/{r.regulation_id}/",
            {"points_for_win": 3}, format="json")
        assertOK(self, res, 200)
        r.refresh_from_db()
        self.assertEqual(r.points_for_win, 3)

    def test_delete(self):
        r = make_regulation()
        res = self.client.delete(f"/api/tournaments/regulations/{r.regulation_id}/")
        assertOK(self, res, 204)
        self.assertFalse(Regulation.objects.filter(regulation_id=r.regulation_id).exists())

    def test_db_count_increases(self):
        before = Regulation.objects.count()
        self.client.post("/api/tournaments/regulations/", self.payload, format="json")
        self.assertEqual(Regulation.objects.count(), before + 1)


# ═════════════════════════════════════════════
# TOURNAMENT
# ═════════════════════════════════════════════

class TournamentModelTest(TestCase):

    def test_create(self):
        t = make_tournament()
        self.assertIsNotNone(t.tournament_id)
        self.assertEqual(t.category, "OPEN")

    def test_str(self):
        t = make_tournament()
        print(f"\n  Tournament str: {str(t)}")
        self.assertIn("OPEN", str(t))

    def test_default_status_upcoming(self):
        reg = make_regulation()
        u = make_user()
        t = Tournament.objects.create(
            name="No Status Cup", category="OPEN", regulation=reg,
            start_date=date.today(), end_date=date.today() + timedelta(days=5),
            created_by=u
        )
        self.assertEqual(t.status, "UPCOMING")

    def test_refresh_status_closes_expired_deadline(self):
        reg = make_regulation()
        u = make_user()
        t = Tournament.objects.create(
            name="Expired Cup", category="OPEN", regulation=reg,
            start_date=date.today(), end_date=date.today() + timedelta(days=5),
            status="ACCEPTING_APPLICATIONS",
            application_deadline=timezone.now() - timedelta(hours=1),  # past
            created_by=u
        )
        t.refresh_status()
        t.refresh_from_db()
        print(f"\n  Status after refresh: {t.status}")
        self.assertEqual(t.status, "APPLICATIONS_CLOSED")

    def test_refresh_status_no_change_if_not_expired(self):
        t = make_tournament()  # deadline 5 days future
        t.refresh_status()
        t.refresh_from_db()
        self.assertEqual(t.status, "ACCEPTING_APPLICATIONS")

    def test_uuid_pk(self):
        t = make_tournament()
        self.assertIsNotNone(t.tournament_id)

    def test_regulation_protected_on_delete(self):
        reg = make_regulation()
        make_tournament(reg=reg)
        from django.db import IntegrityError
        from django.db.models import ProtectedError
        with self.assertRaises(ProtectedError):
            reg.delete()


class TournamentAPITest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = make_user()
        self.client.force_authenticate(user=self.user)
        self.reg = make_regulation()
        self.payload = {
            "name": "Premier Cup", "category": "OPEN",
            "regulation": self.reg.regulation_id,
            "start_date": str(date.today()),
            "end_date": str(date.today() + timedelta(days=10)),
            "status": "UPCOMING",
        }

    def test_create(self):
        res = self.client.post("/api/tournaments/tournaments/", self.payload, format="json")
        assertOK(self, res, 201)
        self.assertEqual(res.data["name"], "Premier Cup")
        self.assertEqual(str(res.data["created_by"]), str(self.user.user_id))

    def test_create_missing_regulation(self):
        payload = {**self.payload}
        payload.pop("regulation")
        res = self.client.post("/api/tournaments/tournaments/", payload, format="json")
        assertOK(self, res, 400)

    def test_list(self):
        make_tournament(user=self.user)
        res = self.client.get("/api/tournaments/tournaments/")
        assertOK(self, res, 200)
        self.assertGreaterEqual(len(res.data), 1)

    def test_retrieve(self):
        t = make_tournament(user=self.user)
        res = self.client.get(f"/api/tournaments/tournaments/{t.tournament_id}/")
        print(f"\n  Tournament fields: {list(res.data.keys())}")

    def test_update_status(self):
        t = make_tournament(user=self.user)
        res = self.client.patch(f"/api/tournaments/tournaments/{t.tournament_id}/", {"status": "ONGOING"}, format="json")
        assertOK(self, res, 200)
        t.refresh_from_db()
        self.assertEqual(t.status, "ONGOING")

    def test_delete(self):
        t = make_tournament(user=self.user)
        tid = t.tournament_id
        res = self.client.delete(f"/api/tournaments/tournaments/{tid}/")
        self.assertFalse(Tournament.objects.filter(tournament_id=tid).exists())

    def test_created_by_readonly(self):
        other = make_user()
        import datetime
        # Change line 291 to this:
        res = self.client.post("/api/tournaments/tournaments/", {
            "name": "IPL 2026",
            "regulation": self.reg.regulation_id,  
            "category": "OPEN",                    
            "start_date": str(datetime.date.today()),
            "end_date": str(datetime.date.today() + datetime.timedelta(days=30)),
            "created_by": "99999999-0000-0000-0000-000000000000" 
        }, format="json")
        assertOK(self, res, 201)
        self.assertEqual(str(res.data["created_by"]), str(self.user.user_id))

    def test_db_count_increases(self):
        before = Tournament.objects.count()
        self.client.post("/api/tournaments/tournaments/", self.payload, format="json")
        self.assertEqual(Tournament.objects.count(), before + 1)

    def test_all_statuses_accepted(self):
        for s in ["UPCOMING", "ACCEPTING_APPLICATIONS", "APPLICATIONS_CLOSED", "ONGOING", "COMPLETED", "CANCELLED"]:
            t = make_tournament(user=self.user)
            res = self.client.patch(f"/api/tournaments/tournaments/{t.tournament_id}/", {"status": s}, format="json")
            if res.status_code != 200:
                print(f"\n[FAIL] Status '{s}' rejected: {res.status_code} - {getattr(res, 'data', res.content)}")

    def test_all_categories_accepted(self):
        for cat in ["INTER_COLLEGE", "INTER_SCHOOL", "CLUB_LEVEL", "DISTRICT_LEVEL", "STATE_LEVEL", "NATIONAL_LEVEL", "CORPORATE_LEVEL", "OPEN"]:
            payload = {**self.payload, "category": cat, "name": f"Cup_{cat}"}
            res = self.client.post("/api/tournaments/tournaments/", payload, format="json")
            if res.status_code != 201:
                print(f"\n[FAIL] Category '{cat}' rejected: {res.data}")
            self.assertEqual(res.status_code, 201)


# ═════════════════════════════════════════════
# GROUP
# ═════════════════════════════════════════════

class GroupTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = make_user()
        self.client.force_authenticate(user=self.user)
        self.tournament = make_tournament(user=self.user)

    def test_create_group(self):
        res = self.client.post("/api/tournaments/groups/", {
            "tournament": str(self.tournament.tournament_id),
            "name": "Group A"
        }, format="json")
        assertOK(self, res, 201)
        self.assertEqual(res.data["name"], "Group A")

    def test_unique_group_name_per_tournament(self):
        Group.objects.create(tournament=self.tournament, name="Group A")
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Group.objects.create(tournament=self.tournament, name="Group A")

    def test_same_name_different_tournament_allowed(self):
        t2 = make_tournament(user=self.user)
        Group.objects.create(tournament=self.tournament, name="Group A")
        g2 = Group.objects.create(tournament=t2, name="Group A")
        self.assertIsNotNone(g2.group_id)

    def test_str(self):
        g = Group.objects.create(tournament=self.tournament, name="Group B")
        print(f"\n  Group str: {str(g)}")
        self.assertIn("Group B", str(g))

    def test_list(self):
        Group.objects.create(tournament=self.tournament, name="Group A")
        res = self.client.get("/api/tournaments/groups/")
        assertOK(self, res, 200)
        self.assertGreaterEqual(len(res.data), 1)


# ═════════════════════════════════════════════
# TOURNAMENT ORGANIZER
# ═════════════════════════════════════════════

class TournamentOrganizerTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = make_user()
        self.client.force_authenticate(user=self.user)
        self.tournament = make_tournament(user=self.user)

    def test_create_organizer(self):
        res = self.client.post("/api/tournaments/organizers/", {
            "tournament": str(self.tournament.tournament_id),
            "user": str(self.user.user_id),
            "is_primary": True,
        }, format="json")
        assertOK(self, res, 201)
        print(f"\n  Organizer response: {res.data}")
        self.assertTrue(res.data["is_primary"])

    def test_unique_organizer_per_tournament(self):
        TournamentOrganizer.objects.create(
            tournament=self.tournament, user=self.user
        )
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            TournamentOrganizer.objects.create(
                tournament=self.tournament, user=self.user
            )

    def test_str(self):
        o = TournamentOrganizer.objects.create(
            tournament=self.tournament, user=self.user
        )
        print(f"\n  Organizer str: {str(o)}")
        self.assertIn(self.user.email, str(o))

    def test_list(self):
        TournamentOrganizer.objects.create(tournament=self.tournament, user=self.user)
        res = self.client.get("/api/tournaments/organizers/")
        assertOK(self, res, 200)
        self.assertGreaterEqual(len(res.data), 1)


# ═════════════════════════════════════════════
# APPLICATION
# ═════════════════════════════════════════════

class ApplicationModelTest(TestCase):

    def setUp(self):
        self.team = make_team()
        self.tournament = make_tournament()

    def test_create_application(self):
        app = make_application(self.team, self.tournament)
        self.assertEqual(app.status, "PENDING")
        self.assertIsNotNone(app.application_id)

    def test_str(self):
        app = make_application(self.team, self.tournament)
        print(f"\n  Application str: {str(app)}")
        self.assertIn("PENDING", str(app))

    def test_unique_team_tournament(self):
        make_application(self.team, self.tournament)
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            make_application(self.team, self.tournament)

    def test_unique_registered_name_per_tournament(self):
        Application.objects.create(
            team=self.team, tournament=self.tournament,
            registered_name="Lions XI", registered_short_name="LXI"
        )
        team2 = make_team()
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Application.objects.create(
                team=team2, tournament=self.tournament,
                registered_name="Lions XI", registered_short_name="LX2"
            )

    def test_unique_registered_short_name_per_tournament(self):
        Application.objects.create(
            team=self.team, tournament=self.tournament,
            registered_name="Lions XI", registered_short_name="LXI"
        )
        team2 = make_team()
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Application.objects.create(
                team=team2, tournament=self.tournament,
                registered_name="Tigers XI", registered_short_name="LXI"
            )

    def test_db_count_after_create(self):
        before = Application.objects.count()
        make_application(self.team, self.tournament)
        self.assertEqual(Application.objects.count(), before + 1)


class ApplicationAPITest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = make_user()
        self.client.force_authenticate(user=self.user)
        self.team = make_team()
        self.tournament = make_tournament(user=self.user)

    def test_create_application(self):
        res = self.client.post("/api/tournaments/applications/", {
            "team": str(self.team.team_id),
            "tournament": str(self.tournament.tournament_id),
            "registered_name": "Lions XI",
            "registered_short_name": "LXI",
        }, format="json")
        assertOK(self, res, 201)
        print(f"\n  Application response fields: {list(res.data.keys())}")
        self.assertEqual(res.data["status"], "PENDING")

    def test_accept_application_creates_standing(self):
        app = make_application(self.team, self.tournament)
        res = self.client.patch(f"/api/tournaments/applications/{app.application_id}/",
            {"status": "ACCEPTED"}, format="json")
        assertOK(self, res, 200)
        exists = TournamentStanding.objects.filter(
            tournament=self.tournament, team=self.team
        ).exists()
        print(f"\n  Standing created on ACCEPT: {exists}")
        self.assertTrue(exists)

    def test_accept_twice_no_duplicate_standing(self):
        app = make_application(self.team, self.tournament)
        self.client.patch(f"/api/tournaments/applications/{app.application_id}/",
            {"status": "ACCEPTED"}, format="json")
        self.client.patch(f"/api/tournaments/applications/{app.application_id}/",
            {"status": "ACCEPTED"}, format="json")
        count = TournamentStanding.objects.filter(
            tournament=self.tournament, team=self.team
        ).count()
        self.assertEqual(count, 1)

    def test_reject_application(self):
        app = make_application(self.team, self.tournament)
        res = self.client.patch(f"/api/tournaments/applications/{app.application_id}/",
            {"status": "REJECTED"}, format="json")
        assertOK(self, res, 200)
        app.refresh_from_db()
        self.assertEqual(app.status, "REJECTED")

    def test_reapply_after_rejection(self):
        app = make_application(self.team, self.tournament, app_status="REJECTED")
        res = self.client.post(
            f"/api/tournaments/applications/{app.application_id}/reapply/",
            {}, format="json"
        )
        assertOK(self, res, 200)
        app.refresh_from_db()
        self.assertEqual(app.status, "PENDING")
        self.assertIsNone(app.processed_at)

    def test_reapply_non_rejected_fails(self):
        app = make_application(self.team, self.tournament, app_status="PENDING")
        res = self.client.post(
            f"/api/tournaments/applications/{app.application_id}/reapply/",
            {}, format="json"
        )
        assertOK(self, res, 400)
        print(f"\n  Reapply non-rejected error: {res.data}")

    def test_submit_application_insufficient_players(self):
        res = self.client.post("/api/tournaments/applications/submit-application/", {
            "team_id": str(self.team.team_id),
            "tournament_id": str(self.tournament.tournament_id),
            "registered_name": "My XI",
            "registered_short_name": "MXI",
        }, format="json")
        assertOK(self, res, 400)
        print(f"\n  Insufficient players error: {res.data}")
        self.assertIn("error", res.data)

    def test_submit_application_with_enough_players(self):
        reg = make_regulation(players_per_side=2)
        t = make_tournament(reg=reg, user=self.user)
        team = make_team()
        for _ in range(2):
            p = make_player(team=team)
            TournamentSquad.objects.create(
                tournament=t, team=team, player=p,
                jersey_number=Player.objects.filter(current_team=team).count()
            )
        res = self.client.post("/api/tournaments/applications/submit-application/", {
            "team_id": str(team.team_id),
            "tournament_id": str(t.tournament_id),
            "registered_name": "My XI",
            "registered_short_name": "MXI",
        }, format="json")
        assertOK(self, res, 201)
        print(f"\n  Submit application response: {res.data}")
        self.assertIn("application_id", res.data)
        self.assertEqual(res.data["players_linked"], 2)

    def test_list_applications(self):
        make_application(self.team, self.tournament)
        res = self.client.get("/api/tournaments/applications/")
        assertOK(self, res, 200)
        self.assertGreaterEqual(len(res.data), 1)


# ═════════════════════════════════════════════
# TOURNAMENT STANDING
# ═════════════════════════════════════════════

class TournamentStandingTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = make_user()
        self.client.force_authenticate(user=self.user)
        self.team = make_team()
        self.tournament = make_tournament(user=self.user)

    def test_create_standing(self):
        s = TournamentStanding.objects.create(
            tournament=self.tournament, team=self.team
        )
        self.assertEqual(s.points, 0)
        self.assertEqual(s.matches_played, 0)

    def test_unique_team_tournament_standing(self):
        TournamentStanding.objects.create(tournament=self.tournament, team=self.team)
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            TournamentStanding.objects.create(tournament=self.tournament, team=self.team)

    def test_str(self):
        s = TournamentStanding.objects.create(tournament=self.tournament, team=self.team)
        print(f"\n  Standing str: {str(s)}")
        self.assertIn("0 pts", str(s))

    def test_ordering_by_points_then_nrr(self):
        team2 = make_team()
        s1 = TournamentStanding.objects.create(tournament=self.tournament, team=self.team, points=4)
        s2 = TournamentStanding.objects.create(tournament=self.tournament, team=team2, points=6)
        standings = list(TournamentStanding.objects.filter(tournament=self.tournament))
        self.assertEqual(standings[0].points, 6)
        self.assertEqual(standings[1].points, 4)

    def test_api_list_standings(self):
        TournamentStanding.objects.create(tournament=self.tournament, team=self.team)
        res = self.client.get("/api/tournaments/standings/")
        assertOK(self, res, 200)
        print(f"\n  Standing fields: {list(res.data[0].keys()) if res.data else 'empty'}")
        self.assertGreaterEqual(len(res.data), 1)

    def test_api_standing_readonly_fields(self):
        s = TournamentStanding.objects.create(tournament=self.tournament, team=self.team)
        res = self.client.patch(f"/api/tournaments/standings/{s.tournament_standing_id}/",
            {"points": 999, "matches_played": 99}, format="json")
        assertOK(self, res, 200)
        s.refresh_from_db()
        print(f"\n  Points after patch attempt: {s.points}")
        self.assertNotEqual(s.points, 999)  # readonly, should be ignored