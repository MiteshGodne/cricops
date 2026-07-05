import { useEffect, useRef, useState } from 'react';
import { useLiveScore } from '../hooks/useLiveScore';

export default function LiveScoreWidget({ matchId }) {
  const { score, error } = useLiveScore(matchId);
  const [flash, setFlash] = useState(false);
  const prevScore = useRef(null);

  useEffect(() => {
    if (score && prevScore.current !== null && prevScore.current !== score.total_score) {
      setFlash(true);
      const t = setTimeout(() => setFlash(false), 700);
      return () => clearTimeout(t);
    }
    if (score) prevScore.current = score.total_score;
  }, [score?.total_score]);

  if (error) return <p className="text-sm text-gray-400 italic">{error}</p>;
  if (!score) return <p className="text-sm text-gray-400 animate-pulse">Loading score...</p>;

  const striker = score.current_batsmen.find(b => b.is_striker);
  const nonStriker = score.current_batsmen.find(b => !b.is_striker);

  return (
    <div className={`relative rounded-2xl overflow-hidden mt-3 shadow-lg border transition-all duration-500 ${flash ? 'ring-4 ring-green-400 scale-[1.01]' : 'ring-0'} mb-3`}>
      <div className="bg-gradient-to-r from-slate-900 via-slate-800 to-slate-900 text-white px-4 py-3 grid grid-cols-3 items-center">
        {/* Batting side */}
        <div className="text-left">
          <p className="text-[10px] text-slate-400">Innings Number : {score.innings_number}</p>
          <p className="text-[10px] uppercase tracking-wider text-green-400 font-semibold mb-1">Batting</p>
          <p className="font-bold text-sm truncate">{score.batting_team}</p>
          <div className="mt-1 space-y-0.5 text-xs text-slate-300">
            {striker && <p>⭐ {striker.player_name} {striker.runs}({striker.balls_faced})</p>}
            {nonStriker && <p className="opacity-70">{nonStriker.player_name} {nonStriker.runs}({nonStriker.balls_faced})</p>}
          </div>
        </div>

        {/* Score center */}
        <div className="text-center">
          <p className={`text-3xl font-extrabold tracking-tight transition-transform duration-500 ${flash ? 'scale-110 text-green-400' : ''}`}>
            {score.total_score}<span className="text-lg">/{score.total_wickets}</span>
          </p>
          <div className="text-xs text-slate-400 mt-0.5">
            <p>{score.overs_completed} overs | {score.overs_remaining} overs left <br />
              Current Run Rate : {score.current_run_rate}</p>
          </div>
          {score.target_runs && (
            <p className="text-[11px] text-amber-300 mt-1">
              Needs {score.runs_required} | Required Run Rate {score.required_run_rate}
            </p>
          )}
        </div>

        {/* Bowling side */}
        <div className="text-right">
          <p className="text-[10px] uppercase tracking-wider text-red-400 font-semibold mb-1">Bowling</p>
          <p className="font-bold text-sm truncate">{score.fielding_team}</p>
          <p className="text-xs text-slate-300 mt-1">
            {score.current_bowler.player_name}<br />
            {score.current_bowler.overs}-{score.current_bowler.runs_conceded}-{score.current_bowler.wickets}
          </p>
        </div>
      </div>
      <div className="h-1 w-full bg-gradient-to-r from-green-500 via-yellow-400 to-red-500 animate-pulse" />
    </div>
  );
}