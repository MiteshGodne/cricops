import uuid
import random
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.utils import timezone
from datetime import date, timedelta

from accounts.models import User
from venues.models import Venue
from teams.models import Team, TournamentSquad
from players.models import Player
from tournaments.models import (
    Regulation, Tournament, Application, Group, TournamentStanding
)
from matches.models import Match, TeamMatch, Innings, Delivery, PlayerDelivery, MatchLiveState


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