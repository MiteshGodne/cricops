import { useLiveScore } from '../hooks/useLiveScore';

export default function LiveScoreWidget({ matchId }) {
  const { score, error } = useLiveScore(matchId);

  if (error) return <p className="text-sm text-gray-500">{error}</p>;
  if (!score) return <p>Loading score...</p>;

  return (
    <div className="border rounded p-4 mb-4">
      <h3 className="font-semibold">{score.batting_team} vs {score.fielding_team}</h3>
      <p className="text-2xl font-bold">{score.total_score}/{score.total_wickets} <span className="text-sm font-normal">({score.overs_completed} ov)</span></p>
      {score.target_runs && <p className="text-sm">Target: {score.target_runs} · Need {score.runs_required} (RRR {score.required_run_rate})</p>}
      <div className="flex gap-6 mt-2 text-sm">
        {score.current_batsmen.map((b) => (
          <span key={b.player_id}>{b.player_name}{b.is_striker ? '*' : ''} {b.runs}({b.balls_faced})</span>
        ))}
      </div>
      <p className="text-sm mt-1">{score.current_bowler.player_name}: {score.current_bowler.overs}-{score.current_bowler.runs_conceded}-{score.current_bowler.wickets}</p>
    </div>
  );
}
