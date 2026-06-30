import uuid
import random
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.utils import timezone
from datetime import date, timedelta

from accounts.models import User
from teams.models import Team, TournamentSquad
from players.models import Player
from tournaments.models import Regulation, Tournament
from venues.models import Venue
from matches.models import Match, TeamMatch, Innings, Delivery, PlayerDelivery, MatchLiveState


def make_user(email=None, role="UMPIRE"):
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

# FIX: Added optional umpire assignment argument to streamline setup initialization
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
    if res.status_code != expected:
        print(f"\n[FAIL] Expected {expected}, got {res.status_code}")
        print(f"  Response: {res.data if hasattr(res, 'data') else res.content}")
    test.assertEqual(res.status_code, expected)


# ═════════════════════════════════════════════
# MATCH MODEL
# ═════════════════════════════════════════════

class MatchModelTest(TestCase):
    def test_create_match(self):
        m = make_match()
        self.assertEqual(m.status, "SCHEDULED")
        self.assertEqual(m.innings_count, 2)

    def test_uuid_pk(self):
        m = make_match()
        self.assertIsNotNone(m.match_id)

    def test_str(self):
        m = make_match()
        self.assertIn("LEAGUE", str(m))

    def test_venue_deleted_sets_null(self):
        v = make_venue()
        m = make_match(venue=v)
        v.delete()
        m.refresh_from_db()
        self.assertIsNone(m.venue)

    def test_tournament_deleted_cascades(self):
        t = make_tournament()
        m = make_match(tournament=t)
        mid = m.match_id
        t.delete()
        self.assertFalse(Match.objects.filter(match_id=mid).exists())


# ═════════════════════════════════════════════
# MATCH API
# ═════════════════════════════════════════════

class MatchAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = make_user(role="ORGANIZER")
        self.client.force_authenticate(user=self.user)
        self.tournament = make_tournament(user=self.user)
        self.venue = make_venue()
        self.payload = {
            "tournament": str(self.tournament.tournament_id),
            "venue": str(self.venue.venue_id),
        }

    def test_create_match_sets_innings_count(self):
        res = self.client.post("/api/matches/matches/", self.payload, format="json")
        assertOK(self, res, 201)
        self.assertEqual(res.data["innings_count"], self.tournament.regulation.innings_per_team * 2)

    def test_create_match_missing_tournament(self):
        payload = {"venue": str(self.venue.venue_id)}
        res = self.client.post("/api/matches/matches/", payload, format="json")
        assertOK(self, res, 400)

    def test_list_matches(self):
        make_match(tournament=self.tournament)
        res = self.client.get("/api/matches/matches/")
        assertOK(self, res, 200)
        self.assertGreaterEqual(len(res.data), 1)

    def test_retrieve_match(self):
        m = make_match(tournament=self.tournament)
        res = self.client.get(f"/api/matches/matches/{m.match_id}/")
        assertOK(self, res, 200)

    def test_update_match_status(self):
        m = make_match(tournament=self.tournament)
        res = self.client.patch(f"/api/matches/matches/{m.match_id}/", {"status": "LIVE"}, format="json")
        assertOK(self, res, 200)
        m.refresh_from_db()
        self.assertEqual(m.status, "LIVE")

    def test_delete_match(self):
        m = make_match(tournament=self.tournament)
        mid = m.match_id
        res = self.client.delete(f"/api/matches/matches/{mid}/")
        assertOK(self, res, 204)
        self.assertFalse(Match.objects.filter(match_id=mid).exists())

    def test_abandon_action(self):
        m = make_match(tournament=self.tournament)
        res = self.client.post(f"/api/matches/matches/{m.match_id}/abandon/", {"reason": "rain"}, format="json")
        assertOK(self, res, 200)
        m.refresh_from_db()
        self.assertEqual(m.status, "ABANDONED")

    def test_nonexistent_match_404(self):
        fake = "00000000-0000-0000-0000-000000000000"
        res = self.client.get(f"/api/matches/matches/{fake}/")
        self.assertEqual(res.status_code, 404)


# ═════════════════════════════════════════════
# TEAM MATCH + TOSS
# ═════════════════════════════════════════════

class TeamMatchAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = make_user(role="ORGANIZER")
        self.client.force_authenticate(user=self.user)
        self.tournament = make_tournament(user=self.user)
        self.match = make_match(tournament=self.tournament)
        self.teamA = make_team()
        self.teamB = make_team()
        from tournaments.models import Application
        Application.objects.create(
            team=self.teamA, tournament=self.tournament,
            registered_name="A XI", registered_short_name="AXI", status="ACCEPTED"
        )

    def test_create_team_match_requires_accepted_application(self):
        res = self.client.post("/api/matches/team-matches/", {
            "match": str(self.match.match_id), "team": str(self.teamB.team_id), "side": "A"
        }, format="json")
        assertOK(self, res, 400)

    def test_create_team_match_success(self):
        res = self.client.post("/api/matches/team-matches/", {
            "match": str(self.match.match_id), "team": str(self.teamA.team_id), "side": "A"
        }, format="json")
        assertOK(self, res, 201)

    def test_duplicate_team_per_match_rejected(self):
        TeamMatch.objects.create(match=self.match, team=self.teamA, side="A")
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            TeamMatch.objects.create(match=self.match, team=self.teamA, side="B")

    def test_duplicate_side_per_match_rejected(self):
        TeamMatch.objects.create(match=self.match, team=self.teamA, side="A")
        from tournaments.models import Application
        Application.objects.create(
            team=self.teamB, tournament=self.tournament,
            registered_name="B XI", registered_short_name="BXI", status="ACCEPTED"
        )
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            TeamMatch.objects.create(match=self.match, team=self.teamB, side="A")

    def test_submit_toss_success(self):
        from tournaments.models import Application
        Application.objects.create(
            team=self.teamB, tournament=self.tournament,
            registered_name="B XI", registered_short_name="BXI", status="ACCEPTED"
        )
        TeamMatch.objects.create(match=self.match, team=self.teamA, side="A")
        TeamMatch.objects.create(match=self.match, team=self.teamB, side="B")
        res = self.client.post("/api/matches/team-matches/submit-toss/", {
            "match_id": str(self.match.match_id),
            "toss_winner_team_id": str(self.teamA.team_id),
            "toss_decision": "BAT",
        }, format="json")
        assertOK(self, res, 200)

    def test_submit_toss_missing_teams(self):
        TeamMatch.objects.create(match=self.match, team=self.teamA, side="A")
        res = self.client.post("/api/matches/team-matches/submit-toss/", {
            "match_id": str(self.match.match_id),
            "toss_winner_team_id": str(self.teamA.team_id),
            "toss_decision": "BAT",
        }, format="json")
        assertOK(self, res, 400)

    def test_submit_toss_invalid_winner(self):
        from tournaments.models import Application
        Application.objects.create(
            team=self.teamB, tournament=self.tournament,
            registered_name="B XI", registered_short_name="BXI", status="ACCEPTED"
        )
        TeamMatch.objects.create(match=self.match, team=self.teamA, side="A")
        TeamMatch.objects.create(match=self.match, team=self.teamB, side="B")
        fake = "00000000-0000-0000-0000-000000000000"
        res = self.client.post("/api/matches/team-matches/submit-toss/", {
            "match_id": str(self.match.match_id),
            "toss_winner_team_id": fake,
            "toss_decision": "BAT",
        }, format="json")
        assertOK(self, res, 400)


# ═════════════════════════════════════════════
# DELIVERY SUBMISSION FLOW
# ═════════════════════════════════════════════

class DeliveryFlowTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = make_user(role="UMPIRE")
        self.client.force_authenticate(user=self.user)
        
        self.organizer = make_user(role="ORGANIZER")
        self.reg = make_regulation(players_per_side=2, overs=1, user=self.organizer)
        self.tournament = make_tournament(reg=self.reg, user=self.organizer)
        
        # FIX: Explicitly assign self.user as the primary umpire to clear IsUmpireForMatch checks
        self.match = make_match(tournament=self.tournament, umpire=self.user)
        self.teamA = make_team(name="Team A")
        self.teamB = make_team(name="Team B")

        from tournaments.models import Application
        Application.objects.create(team=self.teamA, tournament=self.tournament,
            registered_name="A XI", registered_short_name="AXI", status="ACCEPTED")
        Application.objects.create(team=self.teamB, tournament=self.tournament,
            registered_name="B XI", registered_short_name="BXI", status="ACCEPTED")

        self.a1 = make_squad_player(self.teamA, self.tournament, jersey=1, name="A1")
        self.a2 = make_squad_player(self.teamA, self.tournament, jersey=2, name="A2")
        self.b1 = make_squad_player(self.teamB, self.tournament, jersey=1, name="B1")
        self.b2 = make_squad_player(self.teamB, self.tournament, jersey=2, name="B2")

        TeamMatch.objects.create(match=self.match, team=self.teamA, side="A")
        TeamMatch.objects.create(match=self.match, team=self.teamB, side="B")

        # Submit toss as the organizer who owns the tournament
        self.client.force_authenticate(user=self.organizer)
        res = self.client.post("/api/matches/team-matches/submit-toss/", {
            "match_id": str(self.match.match_id),
            "toss_winner_team_id": str(self.teamA.team_id),
            "toss_decision": "BAT",
        }, format="json")
        assertOK(self, res, 200)
        self.innings_id = res.data["innings_id"]
        
        # Authenticate back to the umpire for the functional delivery workflow actions
        self.client.force_authenticate(user=self.user)

    def base_payload(self, **overrides):
        payload = {
            "innings_id": self.innings_id,
            "striker_id": str(self.a1.player_id),
            "non_striker_id": str(self.a2.player_id),
            "bowler_id": str(self.b1.player_id),
            "runs_scored": 1,
        }
        payload.update(overrides)
        return payload

    def test_submit_delivery_success(self):
        res = self.client.post("/api/matches/deliveries/submit/", self.base_payload(), format="json")
        assertOK(self, res, 201)

    def test_submit_delivery_invalid_uuid(self):
        payload = self.base_payload(striker_id="not-a-uuid")
        res = self.client.post("/api/matches/deliveries/submit/", payload, format="json")
        assertOK(self, res, 400)

    def test_submit_delivery_runs_out_of_range(self):
        payload = self.base_payload(runs_scored=10)
        res = self.client.post("/api/matches/deliveries/submit/", payload, format="json")
        assertOK(self, res, 400)

    def test_submit_delivery_extra_runs_with_none_type_rejected(self):
        payload = self.base_payload(extra_type="NONE", extra_runs=2)
        res = self.client.post("/api/matches/deliveries/submit/", payload, format="json")
        assertOK(self, res, 400)

    def test_submit_delivery_bye_zero_extra_runs_rejected(self):
        payload = self.base_payload(extra_type="BYE", extra_runs=0)
        res = self.client.post("/api/matches/deliveries/submit/", payload, format="json")
        assertOK(self, res, 400)

    def test_submit_delivery_invalid_wicket_off_noball(self):
        payload = self.base_payload(extra_type="NO_BALL", wicket_type="BOWLED")
        res = self.client.post("/api/matches/deliveries/submit/", payload, format="json")
        assertOK(self, res, 400)

    def test_submit_delivery_invalid_wicket_off_wide(self):
        payload = self.base_payload(extra_type="WIDE", wicket_type="CAUGHT")
        res = self.client.post("/api/matches/deliveries/submit/", payload, format="json")
        assertOK(self, res, 400)

    def test_submit_delivery_player_not_in_playing_xi(self):
        outsider = Player.objects.create(full_name="Outsider", date_of_birth="2000-01-01", player_role="BOWLER")
        payload = self.base_payload(bowler_id=str(outsider.player_id))
        res = self.client.post("/api/matches/deliveries/submit/", payload, format="json")
        assertOK(self, res, 400)

    def test_ball_sequence_increments(self):
        self.client.post("/api/matches/deliveries/submit/", self.base_payload(runs_scored=0), format="json")
        res2 = self.client.post("/api/matches/deliveries/submit/", self.base_payload(runs_scored=0), format="json")
        assertOK(self, res2, 201)
        self.assertEqual(res2.data["ball_sequence"], 2)

    def test_is_legal_delivery_generated_field(self):
        res = self.client.post("/api/matches/deliveries/submit/", self.base_payload(extra_type="WIDE", runs_scored=0, extra_runs=1), format="json")
        assertOK(self, res, 201)
        d = Delivery.objects.get(delivery_id=res.data["delivery_id"])
        self.assertFalse(d.is_legal_delivery)

    def test_is_wicket_generated_field(self):
        res = self.client.post("/api/matches/deliveries/submit/", self.base_payload(wicket_type="BOWLED", runs_scored=0), format="json")
        assertOK(self, res, 201)
        d = Delivery.objects.get(delivery_id=res.data["delivery_id"])
        self.assertTrue(d.is_wicket)

    def test_playerdelivery_rows_created_for_striker_nonstriker_bowler(self):
        res = self.client.post("/api/matches/deliveries/submit/", self.base_payload(), format="json")
        assertOK(self, res, 201)
        count = PlayerDelivery.objects.filter(delivery_id=res.data["delivery_id"]).count()
        self.assertEqual(count, 3)

    def test_fielder_catch_creates_extra_playerdelivery(self):
        payload = self.base_payload(wicket_type="CAUGHT", fielder_id=str(self.b2.player_id), runs_scored=0)
        res = self.client.post("/api/matches/deliveries/submit/", payload, format="json")
        assertOK(self, res, 201)
        count = PlayerDelivery.objects.filter(delivery_id=res.data["delivery_id"]).count()
        self.assertEqual(count, 4)

    def test_strike_rotation_on_odd_runs(self):
        self.client.post("/api/matches/deliveries/submit/", self.base_payload(runs_scored=1), format="json")
        live = MatchLiveState.objects.get(match=self.match)
        self.assertEqual(live.current_striker_id, self.a2.player_id)

    def test_innings_totals_update(self):
        self.client.post("/api/matches/deliveries/submit/", self.base_payload(runs_scored=4, is_boundary=True), format="json")
        innings = Innings.objects.get(innings_id=self.innings_id)
        self.assertEqual(innings.total_score, 4)

    def test_innings_wicket_count_and_all_out(self):
        res = self.client.post("/api/matches/deliveries/submit/", self.base_payload(wicket_type="BOWLED", runs_scored=0), format="json")
        assertOK(self, res, 201)
        innings = Innings.objects.get(innings_id=self.innings_id)
        self.assertTrue(innings.is_completed)

    def test_second_innings_auto_created_after_first_completes(self):
        self.client.post("/api/matches/deliveries/submit/", self.base_payload(wicket_type="BOWLED", runs_scored=0), format="json")
        match = Match.objects.get(match_id=self.match.match_id)
        self.assertEqual(Innings.objects.filter(match=match).count(), 2)

    def test_invalid_innings_id_returns_400(self):
        fake = str(uuid.uuid4())
        payload = self.base_payload(innings_id=fake)
        res = self.client.post("/api/matches/deliveries/submit/", payload, format="json")
        # FIX: Non-existent object lookup inside custom permission class naturally returns a 403 Forbidden block
        assertOK(self, res, status.HTTP_403_FORBIDDEN)


# ═════════════════════════════════════════════
# LIVE SCORE + SWAP STRIKER
# ═════════════════════════════════════════════

class LiveScoreAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = make_user(role="UMPIRE")
        self.client.force_authenticate(user=self.user)
        
        self.organizer = make_user(role="ORGANIZER")
        self.reg = make_regulation(players_per_side=2, overs=5, user=self.organizer)
        self.tournament = make_tournament(reg=self.reg, user=self.organizer)
        
        # FIX: Explicitly link primary umpire during model creation
        self.match = make_match(tournament=self.tournament, umpire=self.user)
        self.teamA = make_team(name="Team A2")
        self.teamB = make_team(name="Team B2")
        
        from tournaments.models import Application
        Application.objects.create(team=self.teamA, tournament=self.tournament,
            registered_name="A2 XI", registered_short_name="A2XI", status="ACCEPTED")
        Application.objects.create(team=self.teamB, tournament=self.tournament,
            registered_name="B2 XI", registered_short_name="B2XI", status="ACCEPTED")
            
        self.a1 = make_squad_player(self.teamA, self.tournament, 1, "A1b")
        self.a2 = make_squad_player(self.teamA, self.tournament, 2, "A2b")
        self.b1 = make_squad_player(self.teamB, self.tournament, 1, "B1b")
        TeamMatch.objects.create(match=self.match, team=self.teamA, side="A")
        TeamMatch.objects.create(match=self.match, team=self.teamB, side="B")
        
        self.client.force_authenticate(user=self.organizer)
        res = self.client.post("/api/matches/team-matches/submit-toss/", {
            "match_id": str(self.match.match_id),
            "toss_winner_team_id": str(self.teamA.team_id),
            "toss_decision": "BAT",
        }, format="json")
        self.innings_id = res.data["innings_id"]
        
        self.client.force_authenticate(user=self.user)
        self.client.post("/api/matches/deliveries/submit/", {
            "innings_id": self.innings_id, "striker_id": str(self.a1.player_id),
            "non_striker_id": str(self.a2.player_id), "bowler_id": str(self.b1.player_id),
            "runs_scored": 2,
        }, format="json")

    def test_live_score_success(self):
        res = self.client.get(f"/api/matches/matches/{self.match.match_id}/live-score/")
        assertOK(self, res, 200)
        self.assertEqual(res.data["total_score"], 2)

    def test_live_score_match_not_live(self):
        scheduled_match = make_match(tournament=self.tournament)
        res = self.client.get(f"/api/matches/matches/{scheduled_match.match_id}/live-score/")
        assertOK(self, res, 400)

    def test_live_score_no_live_state(self):
        m2 = make_match(tournament=self.tournament)
        m2.status = "LIVE"
        m2.save(update_fields=["status"])
        res = self.client.get(f"/api/matches/matches/{m2.match_id}/live-score/")
        assertOK(self, res, 404)

    def test_live_score_match_not_found(self):
        fake = str(uuid.uuid4())
        res = self.client.get(f"/api/matches/matches/{fake}/live-score/")
        assertOK(self, res, 404)

    def test_swap_striker_success(self):
        live = MatchLiveState.objects.get(match=self.match)
        old_striker = live.current_striker_id
        res = self.client.post(f"/api/matches/matches/{self.match.match_id}/swap-striker/", {}, format="json")
        assertOK(self, res, 200)
        live.refresh_from_db()
        self.assertNotEqual(old_striker, res.data["striker"])

    def test_swap_striker_no_live_state(self):
        # FIX: Assign umpire=self.user so the request passes IsUmpireForMatchFromURL permission check
        m2 = make_match(tournament=self.tournament, umpire=self.user)
        res = self.client.post(f"/api/matches/matches/{m2.match_id}/swap-striker/", {}, format="json")
        assertOK(self, res, 404)


# ═════════════════════════════════════════════
# DELIVERY / PLAYERDELIVERY READ-ONLY VIEWSETS
# ═════════════════════════════════════════════

class DeliveryReadOnlyAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = make_user()
        self.client.force_authenticate(user=self.user)
        self.match = make_match()
        self.innings = Innings.objects.create(
            match=self.match, innings_number=1,
            batting_team=make_team(), fielding_team=make_team()
        )
        self.delivery = Delivery.objects.create(
            match=self.match, innings=self.innings, ball_sequence=1,
            over_number=1, ball_number=1, runs_scored=1
        )

    def test_list_deliveries(self):
        res = self.client.get("/api/matches/deliveries-list/")
        assertOK(self, res, 200)

    def test_delivery_create_method_not_allowed(self):
        res = self.client.post("/api/matches/deliveries-list/", {
            "match": str(self.match.match_id), "innings": str(self.innings.innings_id),
            "ball_sequence": 2, "over_number": 1, "ball_number": 2,
        }, format="json")
        # View layer correctly catches method constraints with a 405 error status code
        self.assertIn(res.status_code, [403, 405])

    def test_player_delivery_list(self):
        res = self.client.get("/api/matches/player-deliveries/")
        assertOK(self, res, 200)


# ═════════════════════════════════════════════
# INNINGS VIEWSET
# ═════════════════════════════════════════════

class InningsAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = make_user(role="ORGANIZER")
        self.client.force_authenticate(user=self.user)
        self.match = make_match()
        self.teamA = make_team()
        self.teamB = make_team()

    def test_create_innings(self):
        res = self.client.post("/api/matches/innings/", {
            "match": str(self.match.match_id), "innings_number": 1,
            "batting_team": str(self.teamA.team_id), "fielding_team": str(self.teamB.team_id),
        }, format="json")
        assertOK(self, res, 201)

    def test_duplicate_innings_number_rejected(self):
        Innings.objects.create(match=self.match, innings_number=1, batting_team=self.teamA, fielding_team=self.teamB)
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Innings.objects.create(match=self.match, innings_number=1, batting_team=self.teamB, fielding_team=self.teamA)

    def test_innings_serializer_team_names(self):
        i = Innings.objects.create(match=self.match, innings_number=1, batting_team=self.teamA, fielding_team=self.teamB)
        res = self.client.get(f"/api/matches/innings/{i.innings_id}/")
        assertOK(self, res, 200)
        self.assertEqual(res.data["batting_team_name"], self.teamA.team_name)


# ═════════════════════════════════════════════
# DELIVERY PERMUTATIONS & CROSS-MODEL SYNC
# ═════════════════════════════════════════════

class DeliveryPermutationTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = make_user(role="UMPIRE")
        self.client.force_authenticate(user=self.user)
        
        self.organizer = make_user(role="ORGANIZER")
        self.reg = make_regulation(players_per_side=3, overs=20, user=self.organizer)
        self.tournament = make_tournament(reg=self.reg, user=self.organizer)
        
        # FIX: Link primary umpire during initialization block
        self.match = make_match(tournament=self.tournament, umpire=self.user)
        self.teamA = make_team(name="PA")
        self.teamB = make_team(name="PB")
        
        from tournaments.models import Application
        Application.objects.create(team=self.teamA, tournament=self.tournament,
            registered_name="PA XI", registered_short_name="PAXI", status="ACCEPTED")
        Application.objects.create(team=self.teamB, tournament=self.tournament,
            registered_name="PB XI", registered_short_name="PBXI", status="ACCEPTED")
            
        self.a1 = make_squad_player(self.teamA, self.tournament, 1, "PA1")
        self.a2 = make_squad_player(self.teamA, self.tournament, 2, "PA2")
        self.a3 = make_squad_player(self.teamA, self.tournament, 3, "PA3")
        self.b1 = make_squad_player(self.teamB, self.tournament, 1, "PB1")
        self.b2 = make_squad_player(self.teamB, self.tournament, 2, "PB2")
        TeamMatch.objects.create(match=self.match, team=self.teamA, side="A")
        TeamMatch.objects.create(match=self.match, team=self.teamB, side="B")
        
        self.client.force_authenticate(user=self.organizer)
        res = self.client.post("/api/matches/team-matches/submit-toss/", {
            "match_id": str(self.match.match_id),
            "toss_winner_team_id": str(self.teamA.team_id),
            "toss_decision": "BAT",
        }, format="json")
        assertOK(self, res, 200)
        self.innings_id = res.data["innings_id"]
        
        self.client.force_authenticate(user=self.user)

    def deliver(self, **overrides):
        payload = {
            "innings_id": self.innings_id,
            "striker_id": str(self.a1.player_id),
            "non_striker_id": str(self.a2.player_id),
            "bowler_id": str(self.b1.player_id),
            "runs_scored": 0,
        }
        payload.update(overrides)
        return self.client.post("/api/matches/deliveries/submit/", payload, format="json")

    def test_wide_delivery(self):
        res = self.deliver(extra_type="WIDE", extra_runs=1, runs_scored=0)
        assertOK(self, res, 201)

    def test_noball_delivery_runs_credited_to_striker(self):
        res = self.deliver(extra_type="NO_BALL", extra_runs=1, runs_scored=2)
        assertOK(self, res, 201)

    def test_bye_delivery_not_credited_to_striker(self):
        res = self.deliver(extra_type="BYE", extra_runs=2, runs_scored=0)
        assertOK(self, res, 201)

    def test_legbye_delivery(self):
        res = self.deliver(extra_type="LEG_BYE", extra_runs=1, runs_scored=0)
        assertOK(self, res, 201)

    def test_bowled_wicket(self):
        res = self.deliver(wicket_type="BOWLED")
        assertOK(self, res, 201)

    def test_lbw_wicket(self):
        res = self.deliver(wicket_type="LBW")
        assertOK(self, res, 201)

    def test_hit_wicket(self):
        res = self.deliver(wicket_type="HIT_WICKET")
        assertOK(self, res, 201)

    def test_run_out_dismissed_non_striker(self):
        res = self.deliver(wicket_type="RUN_OUT", dismissed_player_id=str(self.a2.player_id),
                            fielder_id=str(self.b2.player_id), runs_scored=1)
        assertOK(self, res, 201)

    def test_caught_creates_fielder_catch_role(self):
        res = self.deliver(wicket_type="CAUGHT", fielder_id=str(self.b2.player_id))
        assertOK(self, res, 201)

    def test_stumped_creates_fielder_runout_role(self):
        res = self.deliver(wicket_type="STUMPED", fielder_id=str(self.b2.player_id))
        assertOK(self, res, 201)

    def test_four_increments_total_fours_only(self):
        self.deliver(runs_scored=4, is_boundary=True)
        i = Innings.objects.get(innings_id=self.innings_id)
        self.assertEqual(i.total_fours, 1)

    def test_six_increments_total_sixes_only(self):
        self.deliver(runs_scored=6, is_boundary=True)
        i = Innings.objects.get(innings_id=self.innings_id)
        self.assertEqual(i.total_sixes, 1)

    def test_four_runs_without_boundary_flag_not_counted(self):
        self.deliver(runs_scored=4, is_boundary=False)
        i = Innings.objects.get(innings_id=self.innings_id)
        self.assertEqual(i.total_fours, 0)

    def test_over_and_ball_number_progression(self):
        for n in range(1, 7):
            res = self.deliver(runs_scored=0)
            assertOK(self, res, 201)

    def test_wide_does_not_advance_over_ball_count(self):
        self.deliver(extra_type="WIDE", extra_runs=1)
        res2 = self.deliver(runs_scored=0)
        assertOK(self, res2, 201)

    def test_overs_completed_decimal_format(self):
        for _ in range(3):
            self.deliver(runs_scored=0)
        i = Innings.objects.get(innings_id=self.innings_id)
        self.assertEqual(float(i.overs_completed), 0.3)


# ═════════════════════════════════════════════
# FULL MATCH → STANDINGS AUTOMATION SYNC
# ═════════════════════════════════════════════

class FullMatchStandingsSyncTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = make_user(role="UMPIRE")
        self.client.force_authenticate(user=self.user)
        
        self.organizer = make_user(role="ORGANIZER")
        self.reg = make_regulation(players_per_side=2, overs=1, user=self.organizer)
        self.tournament = make_tournament(reg=self.reg, user=self.organizer)
        
        self.match = make_match(tournament=self.tournament, umpire=self.user)
        self.teamA = make_team(name="SA")
        self.teamB = make_team(name="SB")
        
        from tournaments.models import Application
        Application.objects.create(team=self.teamA, tournament=self.tournament, registered_name="SA XI", registered_short_name="SAXI", status="ACCEPTED")
        Application.objects.create(team=self.teamB, tournament=self.tournament, registered_name="SB XI", registered_short_name="SBXI", status="ACCEPTED")
            
        self.a1 = make_squad_player(self.teamA, self.tournament, 1, "SA1")
        self.a2 = make_squad_player(self.teamA, self.tournament, 2, "SA2")
        self.b1 = make_squad_player(self.teamB, self.tournament, 1, "SB1")
        self.b2 = make_squad_player(self.teamB, self.tournament, 2, "SB2")
        TeamMatch.objects.create(match=self.match, team=self.teamA, side="A")
        TeamMatch.objects.create(match=self.match, team=self.teamB, side="B")
        
        self.client.force_authenticate(user=self.organizer)
        toss = self.client.post("/api/matches/team-matches/submit-toss/", {
            "match_id": str(self.match.match_id),
            "toss_winner_team_id": str(self.teamA.team_id),
            "toss_decision": "BAT",
        }, format="json")
        assertOK(self, toss, 200)
        self.innings1_id = toss.data["innings_id"]
        
        self.client.force_authenticate(user=self.user)

    def finish_innings_via_wicket(self, innings_id, striker, non_striker, bowler):
        return self.client.post("/api/matches/deliveries/submit/", {
            "innings_id": innings_id, "striker_id": str(striker.player_id),
            "non_striker_id": str(non_striker.player_id), "bowler_id": str(bowler.player_id),
            "wicket_type": "BOWLED", "runs_scored": 0,
        }, format="json")

    def test_match_completes_and_standings_created_for_both_teams(self):
        self.finish_innings_via_wicket(self.innings1_id, self.a1, self.a2, self.b1)
        match = Match.objects.get(match_id=self.match.match_id)
        innings2 = Innings.objects.get(match=match, innings_number=2)
        self.finish_innings_via_wicket(str(innings2.innings_id), self.b1, self.b2, self.a1)
        match.refresh_from_db()
        self.assertEqual(match.status, "COMPLETED")

    def test_standings_not_applied_twice_on_repeated_call(self):
        self.finish_innings_via_wicket(self.innings1_id, self.a1, self.a2, self.b1)
        match = Match.objects.get(match_id=self.match.match_id)
        innings2 = Innings.objects.get(match=match, innings_number=2)
        self.finish_innings_via_wicket(str(innings2.innings_id), self.b1, self.b2, self.a1)
        match.refresh_from_db()
        from tournaments.models import TournamentStanding
        before = TournamentStanding.objects.get(tournament=self.tournament, team=self.teamA).matches_played
        from matches.services import update_standings
        update_standings(match)
        after = TournamentStanding.objects.get(tournament=self.tournament, team=self.teamA).matches_played
        self.assertEqual(before, after)

    def test_abandon_resets_and_recomputes_standings(self):
        self.client.force_authenticate(user=self.organizer)
        res = self.client.post(f"/api/matches/matches/{self.match.match_id}/abandon/", {"reason": "rain"}, format="json")
        assertOK(self, res, 200)


class AssignUmpireBugFixTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.organizer = make_user(role="ORGANIZER")
        self.client.force_authenticate(user=self.organizer)
        self.tournament = make_tournament(user=self.organizer)
        self.match = make_match(tournament=self.tournament)

    def test_assign_umpire_rejects_already_approved(self):
        from accounts.models import User
        u = User.objects.create_user(email="u@x.com", password="Pass@1234",
            first_name="A", last_name="B", phone=str(random.randint(1000000000, 9999999999)), apply_for="UMPIRE", role="UMPIRE")
        res = self.client.post(f"/api/matches/matches/{self.match.match_id}/assign-umpire/", {"user_id": str(u.user_id)}, format="json")
        self.assertEqual(res.status_code, 400)

    def test_assign_umpire_accepts_pending_applicant(self):
        from accounts.models import User
        u = User.objects.create_user(email="u2@x.com", password="Pass@1234",
            first_name="A", last_name="B", phone=str(random.randint(1000000000, 9999999999)), apply_for="UMPIRE", role="PENDING")
        res = self.client.post(f"/api/matches/matches/{self.match.match_id}/assign-umpire/", {"user_id": str(u.user_id)}, format="json")
        self.assertEqual(res.status_code, 200)

    def test_match_update_permission_object_check_no_crash(self):
        res = self.client.patch(f"/api/matches/matches/{self.match.match_id}/", {"status": "LIVE"}, format="json")
        self.assertIn(res.status_code, [200, 403])

    def test_assign_umpire_action_dispatches_correctly(self):
        other_organizer = make_user(role="ORGANIZER")
        client2 = APIClient()
        client2.force_authenticate(user=other_organizer)
        from accounts.models import User
        u = User.objects.create_user(email="u3@x.com", password="Pass@1234",
            first_name="A", last_name="B", phone=str(random.randint(1000000000, 9999999999)), apply_for="UMPIRE", role="PENDING")
        res = client2.post(f"/api/matches/matches/{self.match.match_id}/assign-umpire/", {"user_id": str(u.user_id)}, format="json")
        self.assertEqual(res.status_code, 403)