from django.db import transaction
from django.db.models import Sum, Count, Q
from .models import Delivery, PlayerDelivery, Innings, MatchLiveState
from tournaments.models import TournamentStanding
from players.models import Player
from django.utils import timezone

def get_next_ball_sequence(innings):
    last = Delivery.objects.filter(innings=innings).order_by('-ball_sequence').first()
    return (last.ball_sequence + 1) if last else 1

def calculate_overs(legal_ball_count):
    return f"{legal_ball_count // 6}.{legal_ball_count % 6}"

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

    # calculate over & ball number from legal deliveries
    legal_count = Delivery.objects.filter(
        innings=innings, is_legal_delivery=True
    ).count()
    over_number = (legal_count // 6) + 1
    ball_number = (legal_count % 6) + 1

    # create delivery
    delivery = Delivery.objects.create(
        match=innings.match,
        innings=innings,
        ball_sequence=ball_sequence,
        over_number=over_number,
        ball_number=ball_number,
        runs_scored=runs,
        extra_type=extra_type,
        wicket_type=wicket_type,
    )

    # create player_delivery rows
    player_deliveries = [
        PlayerDelivery(
            delivery=delivery,
            player=striker,
            performance_role='STRIKER',
            runs_attributed=runs if extra_type in ['NONE', 'NO_BALL'] else 0
        ),
        PlayerDelivery(
            delivery=delivery,
            player=non_striker,
            performance_role='NON_STRIKER',
            runs_attributed=0
        ),
        PlayerDelivery(
            delivery=delivery,
            player=bowler,
            performance_role='BOWLER',
            runs_attributed=runs + extra_runs
        ),
    ]
    # add fielder if applicable for wicket 
    if wicket_type in ['CAUGHT', 'STUMPED'] and fielder_id:
        fielder = Player.objects.get(player_id=fielder_id)
        player_deliveries.append(PlayerDelivery(
            delivery=delivery,
            player=fielder,
            performance_role='FIELDER_CATCH' if wicket_type == 'CAUGHT' else 'FIELDER_RUNOUT',
            runs_attributed=0,
            dismissal_info=f"{wicket_type} by {fielder.full_name}"
        ))
    PlayerDelivery.objects.bulk_create(player_deliveries)

    # update innings totals & live state 
    update_innings_totals(innings, wicket_type, runs, extra_runs, extra_type, is_legal)
    update_live_state(innings, striker, non_striker, bowler)
    return delivery

def update_innings_totals(innings, wicket_type, runs, extra_runs, extra_type, is_legal):
    innings.total_score += runs + extra_runs
    if extra_type in ['WIDE', 'NO_BALL']:
        innings.total_extras += extra_runs + 1
    if extra_type == 'WIDE':
        innings.total_wides += 1
    if extra_type == 'NO_BALL':
        innings.total_noballs += 1
    if runs == 4 and extra_type == 'NONE':
        innings.total_fours += 1
    if runs == 6 and extra_type == 'NONE':
        innings.total_sixes += 1
    if wicket_type != 'NONE' and extra_type != 'NO_BALL':
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

    # auto set next innings target when this innings completes
    if just_completed and not target_chased:
        next_innings = Innings.objects.filter(
            match=innings.match, innings_number=innings.innings_number + 1
        ).first()
        if next_innings and not next_innings.target_runs:
            next_innings.target_runs = innings.total_score + 1
            next_innings.save(update_fields=['target_runs'])
            

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
            wickets=Count('id', filter=Q(delivery__is_wicket=True))
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
    runs_required = None
    if innings.target_runs:
        runs_required = innings.target_runs - innings.total_score
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
        'current_batsmen': [striker_data, non_striker_data],
        'current_bowler': bowler_data,
    }

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
        standing.save()
    match.standings_applied = True
    match.save(update_fields=['standings_applied'])