from django.db import transaction
from django.db.models import Sum, Count, Q
from .models import Delivery, PlayerDelivery, Innings, MatchLiveState
from tournaments.models import TournamentStanding
from teams.models import TournamentSquad
from players.models import Player
from django.utils import timezone

def get_next_ball_sequence(innings):
    last = Delivery.objects.filter(innings=innings).order_by('-ball_sequence').first()
    return (last.ball_sequence + 1) if last else 1

def validate_playing_xi(innings, striker, non_striker, bowler):
    tournament = innings.match.tournament
    batting_squad_ids = set(TournamentSquad.objects.filter(
        tournament=tournament, team=innings.batting_team, is_playing_xi=True
    ).values_list('player_id', flat=True))
    fielding_squad_ids = set(TournamentSquad.objects.filter(
        tournament=tournament, team=innings.fielding_team, is_playing_xi=True
    ).values_list('player_id', flat=True))

    if striker.player_id not in batting_squad_ids or non_striker.player_id not in batting_squad_ids:
        raise ValueError("Striker/non-striker must be in batting team's playing XI for this tournament.")
    if bowler.player_id not in fielding_squad_ids:
        raise ValueError("Bowler must be in fielding team's playing XI for this tournament.")

@transaction.atomic
def process_delivery(validated_data):
    innings = Innings.objects.select_related('match', 'batting_team', 'fielding_team').get(
        innings_id=validated_data['innings_id']
    )
    striker = Player.objects.get(player_id=validated_data['striker_id'])
    non_striker = Player.objects.get(player_id=validated_data['non_striker_id'])
    bowler = Player.objects.get(player_id=validated_data['bowler_id'])
    runs = validated_data['runs_scored']
    extra_type = validated_data.get('extra_type', 'NONE')
    extra_runs = validated_data.get('extra_runs', 0)
    wicket_type = validated_data.get('wicket_type', 'NONE')
    fielder_id = validated_data.get('fielder_id')
    dismissed_player_id = validated_data.get('dismissed_player_id')
    ball_sequence = get_next_ball_sequence(innings)
    is_legal = extra_type not in ['WIDE', 'NO_BALL']

    validate_playing_xi(innings, striker, non_striker, bowler)

    legal_count_before = Delivery.objects.filter(innings=innings, is_legal_delivery=True).count()
    over_number = (legal_count_before // 6) + 1
    ball_number = (legal_count_before % 6) + 1

    delivery = Delivery.objects.create(match=innings.match, innings=innings, ball_sequence=ball_sequence,over_number=over_number, ball_number=ball_number, runs_scored=runs,extra_type=extra_type, wicket_type=wicket_type,is_boundary=validated_data.get('is_boundary', False),)

    player_deliveries = [
        PlayerDelivery(delivery=delivery, player=striker, performance_role='STRIKER',
                        runs_attributed=runs if extra_type in ['NONE', 'NO_BALL'] else 0),
        PlayerDelivery(delivery=delivery, player=non_striker, performance_role='NON_STRIKER', runs_attributed=0),
        PlayerDelivery(delivery=delivery, player=bowler, performance_role='BOWLER', runs_attributed=runs + extra_runs),
    ]
    
    dismissed_id = (dismissed_player_id or striker.player_id) if wicket_type != 'NONE' else None
    for pd in player_deliveries:
        if dismissed_id and pd.player_id == dismissed_id:
            pd.dismissal_info = f"{wicket_type}"
    
    if wicket_type in ['CAUGHT', 'STUMPED'] and fielder_id:
        fielder = Player.objects.get(player_id=fielder_id)
        player_deliveries.append(PlayerDelivery(
            delivery=delivery, player=fielder,
            performance_role='FIELDER_CATCH' if wicket_type == 'CAUGHT' else 'FIELDER_RUNOUT',
            runs_attributed=0, dismissal_info=f"{wicket_type} by {fielder.full_name}"
        ))
    PlayerDelivery.objects.bulk_create(player_deliveries)

    update_innings_totals(innings, wicket_type, runs, extra_runs, extra_type, is_legal, is_boundary=validated_data.get('is_boundary', False))

    # auto-rotation logic
    legal_count_after = legal_count_before + (1 if is_legal else 0)
    odd_runs = is_legal and (runs % 2 == 1) and extra_type == 'NONE'
    over_just_ended = is_legal and legal_count_after % 6 == 0
    should_swap = odd_runs != over_just_ended  

    new_striker, new_non_striker = (non_striker, striker) if should_swap else (striker, non_striker)
    update_live_state(innings, new_striker, new_non_striker, bowler)

    return delivery

def update_innings_totals(innings, wicket_type, runs, extra_runs, extra_type, is_legal, is_boundary=False):
    innings.total_score += runs + extra_runs
    if extra_type in ['WIDE', 'NO_BALL']:
        innings.total_extras += extra_runs + 1
    if extra_type == 'WIDE':
        innings.total_wides += 1
    if extra_type == 'NO_BALL':
        innings.total_noballs += 1
    if is_boundary and runs == 4:
        innings.total_fours += 1
    if is_boundary and runs == 6:
        innings.total_sixes += 1
    if wicket_type != 'NONE':
        innings.total_wickets += 1

    legal_count = 0
    if is_legal:
        legal_count = Delivery.objects.filter(innings=innings, is_legal_delivery=True).count()
        innings.overs_completed = float(f"{legal_count // 6}.{legal_count % 6}")

    regulation = innings.match.tournament.regulation
    max_wickets = regulation.players_per_side - 1
    overs_done = bool(regulation.overs_per_innings) and legal_count >= regulation.overs_per_innings * 6
    all_out = innings.total_wickets >= max_wickets
    target_chased = bool(innings.target_runs) and innings.total_score >= innings.target_runs
    just_completed = (overs_done or all_out or target_chased) and not innings.is_completed

    if just_completed:
        innings.is_completed = True
        innings.end_time = timezone.now()

    innings.save(update_fields=[
        'total_score', 'total_wickets', 'total_extras',
        'total_wides', 'total_noballs', 'total_fours',
        'total_sixes', 'overs_completed', 'is_completed', 'end_time'
    ])

    if not just_completed:
        return

    match = innings.match
    total_innings_expected = match.innings_count
    next_innings = Innings.objects.filter(match=match, innings_number=innings.innings_number + 1).first()
    if not next_innings and innings.innings_number < total_innings_expected and not target_chased:
        next_innings = Innings.objects.create(
            match=match,
            innings_number=innings.innings_number + 1,
            batting_team=innings.fielding_team,
            fielding_team=innings.batting_team,
            target_runs=innings.total_score + 1,
        )
        return 
    if next_innings and not target_chased:
        if not next_innings.target_runs:
            next_innings.target_runs = innings.total_score + 1
            next_innings.save(update_fields=['target_runs'])
        return  
    finalize_match_result(match)


def finalize_match_result(match):
    innings_qs = Innings.objects.filter(match=match).order_by('innings_number')
    if innings_qs.count() < match.innings_count or not all(i.is_completed for i in innings_qs):
        return    
    first, second = innings_qs[0], innings_qs[1]
    if first.total_score > second.total_score:
        match.winner_team, match.runnerup_team, match.result_type = first.batting_team, second.batting_team, 'WIN'
    elif second.total_score > first.total_score:
        match.winner_team, match.runnerup_team, match.result_type = second.batting_team, first.batting_team, 'WIN'
    else:
        match.result_type = 'TIE'
        match.winner_team = None
        match.runnerup_team = None
        # regulation.super_over_enabled would trigger Tier 3 super-over flow — not implemented yet

    match.status = 'COMPLETED'
    match.end_date = timezone.now()
    match.save(update_fields=['winner_team', 'runnerup_team', 'result_type', 'status', 'end_date'])
    if match.primary_umpire:
        match.primary_umpire.role = "PENDING"
        match.primary_umpire.save(update_fields = ['role'])
    update_standings(match)
            
def calculate_nrr(tournament, team):
    innings_for = Innings.objects.filter(
        match__tournament=tournament, match__status='COMPLETED', batting_team=team
    )
    innings_against = Innings.objects.filter(
        match__tournament=tournament, match__status='COMPLETED', fielding_team=team
    )
    runs_for = innings_for.aggregate(r=Sum('total_score'))['r'] or 0
    overs_for = sum(float(i.overs_completed) for i in innings_for) or 0.001
    runs_against = innings_against.aggregate(r=Sum('total_score'))['r'] or 0
    overs_against = sum(float(i.overs_completed) for i in innings_against) or 0.001
    return round((runs_for / overs_for) - (runs_against / overs_against), 3)

@transaction.atomic
def update_standings(match):
    if match.status != 'COMPLETED' or match.result_type is None or match.standings_applied:
        return

    regulation = match.tournament.regulation
    team_matches = match.team_matches.select_related('team').all()
    for tm in team_matches:
        standing, _ = TournamentStanding.objects.get_or_create(
            tournament=match.tournament, team=tm.team,
            defaults={'group': match.group}
        )
        standing.matches_played += 1
        if match.result_type == 'TIE':
            standing.matches_tied += 1
            standing.points += regulation.points_for_tie
        elif match.result_type == 'NO_RESULT':
            standing.matches_no_result += 1
            standing.points += regulation.points_for_no_result
        elif match.result_type == 'ABANDONED':
            standing.matches_no_result += 1
            standing.points += regulation.points_for_no_result
        elif match.winner_team_id == tm.team_id:
            standing.matches_won += 1
            standing.points += regulation.points_for_win
        else:
            standing.matches_lost += 1
            standing.points += regulation.points_for_loss
            
        standing.net_run_rate = calculate_nrr(match.tournament, tm.team)
        standing.save()
    match.standings_applied = True
    match.save(update_fields=['standings_applied'])


def update_live_state(innings, striker, non_striker, bowler):
    MatchLiveState.objects.update_or_create(
        match=innings.match,
        defaults={
            'current_innings': innings,
            'current_striker': striker,
            'current_non_striker': non_striker,
            'current_bowler': bowler,
        }
    )
    
#--------------------------------------------------------------------------
    
def calculate_overs(legal_ball_count):
    return f"{legal_ball_count // 6}.{legal_ball_count % 6}"
    
@transaction.atomic
def get_live_score(match):
    live_state = MatchLiveState.objects.select_related(
        'current_innings__batting_team',
        'current_innings__fielding_team',
        'current_striker',
        'current_non_striker',
        'current_bowler'
    ).get(match=match)
    innings = live_state.current_innings
    
    def batsman_stats(player, innings):
        stats = PlayerDelivery.objects.filter(
            player=player,
            delivery__innings=innings,
            performance_role='STRIKER'
        ).aggregate(
            runs=Sum('runs_attributed'),
            balls=Count('id'),
            fours=Count('id', filter=Q(runs_attributed=4)),
            sixes=Count('id', filter=Q(runs_attributed=6)),
        )
        runs = stats['runs'] or 0
        balls = stats['balls'] or 0
        return {
            'player_id': player.player_id,
            'player_name': player.full_name,
            'runs': runs,
            'balls_faced': balls,
            'fours': stats['fours'] or 0,
            'sixes': stats['sixes'] or 0,
            'strike_rate': round((runs / balls * 100), 2) if balls > 0 else 0.0,
        }

    def bowler_stats(player, innings):
        stats = PlayerDelivery.objects.filter(
            player=player,
            delivery__innings=innings,
            performance_role='BOWLER'
        ).aggregate(
            runs=Sum('runs_attributed'),
            wickets=Count('id', filter=Q(delivery__wicket_type__in=['BOWLED','CAUGHT','LBW','STUMPED','HIT_WICKET']))
        )
        legal_balls = Delivery.objects.filter(
            innings=innings,
            is_legal_delivery=True,
            player_deliveries__player=player,
            player_deliveries__performance_role='BOWLER'
        ).count()
        runs = stats['runs'] or 0
        overs_str = calculate_overs(legal_balls)
        overs_float = legal_balls / 6
        return {
            'player_id': player.player_id,
            'player_name': player.full_name,
            'overs': overs_str,
            'runs_conceded': runs,
            'wickets': stats['wickets'] or 0,
            'economy': round(runs / overs_float, 2) if overs_float > 0 else 0.0,
        }
    striker_data = {**batsman_stats(live_state.current_striker, innings), 'is_striker': True}
    non_striker_data = {**batsman_stats(live_state.current_non_striker, innings), 'is_striker': False}
    bowler_data = bowler_stats(live_state.current_bowler, innings)
        
    regulation = match.tournament.regulation

    legal_balls = Delivery.objects.filter(innings=innings, is_legal_delivery=True).count()
    overs_faced = legal_balls / 6 if legal_balls else 0.0

    # current run rate calculation
    current_run_rate = round(innings.total_score / overs_faced, 2) if overs_faced > 0 else 0.0

    runs_required = None
    required_run_rate = None
    if innings.target_runs:
        runs_required = innings.target_runs - innings.total_score
        total_balls_allowed = (regulation.overs_per_innings or 0) * 6
        remaining_balls = total_balls_allowed - legal_balls
        # required run rate calculation
        if remaining_balls > 0 and runs_required > 0:
            required_run_rate = round(runs_required / (remaining_balls / 6), 2)
        else:
            required_run_rate = 0.0
    return {
        'match_id': match.match_id,
        'match_status': match.status,
        'innings_number': innings.innings_number,
        'batting_team': innings.batting_team.team_name,
        'fielding_team': innings.fielding_team.team_name,
        'total_score': innings.total_score,
        'total_wickets': innings.total_wickets,
        'overs_completed': innings.overs_completed,
        'total_extras': innings.total_extras,
        'target_runs': innings.target_runs,
        'runs_required': runs_required,
        'current_run_rate': current_run_rate,
        'required_run_rate': required_run_rate,
        'current_batsmen': [striker_data, non_striker_data],
        'current_bowler': bowler_data,
    }
