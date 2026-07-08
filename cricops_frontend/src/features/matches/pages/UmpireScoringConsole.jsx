import { useParams } from 'react-router-dom';
import { useState, useEffect, useRef } from 'react';
import client from '../../../api/client';
import { ENDPOINTS } from '../../../api/endpoints';
import { useFetch } from '../../../hooks/useFetch';
import { useLiveScore } from '../hooks/useLiveScore';
import LiveScoreWidget from '../components/LiveScoreWidget';
import BallEntryPad from '../components/BallEntryPad';
import TossModal from '../components/TossModal';
import Button from '../../../components/Button';
import BackButton from '../../../components/BackButton';
import { Link } from 'react-router-dom';
import MatchResultBox from '../pages/MatchResultBox';


export default function UmpireScoringConsole() {
  const { matchId } = useParams();
  const { data: match, refetch: refetchMatch } = useFetch(`${ENDPOINTS.MATCHES}${matchId}/`);
  const { data: teamMatchesData } = useFetch(`${ENDPOINTS.TEAM_MATCHES}?match=${matchId}`);
  const teamMatches = Array.isArray(teamMatchesData) ? teamMatchesData : teamMatchesData?.results || [];

  const { score, refetch: refetchScore } = useLiveScore(matchId);
  const [innings, setInnings] = useState(null);
  const [showToss, setShowToss] = useState(false);
  const [striker, setStriker] = useState('');
  const [nonStriker, setNonStriker] = useState('');
  const [bowler, setBowler] = useState('');
  const [squadA, setSquadA] = useState([]);
  const [squadB, setSquadB] = useState([]);
  const [key, setKey] = useState(0);

  const teamA = teamMatches.find((tm) => tm.side === 'A')?.team;
  const teamB = teamMatches.find((tm) => tm.side === 'B')?.team;

  useEffect(() => {
    if (match?.status === 'SCHEDULED' && teamMatches.length === 2) setShowToss(true);
  }, [match, teamMatches]);

  useEffect(() => {
    if (!match) return;
    client.get(`${ENDPOINTS.INNINGS}?match=${matchId}`).then(({ data }) => {
      const list = Array.isArray(data) ? data : data?.results || [];
      const live = list.find((i) => !i.is_completed) || list[list.length - 1];
      setInnings(live);
    });
  }, [matchId, match, key]);

  useEffect(() => {
    if (!innings) return;
    client.get(`${ENDPOINTS.SQUADS}?team=${innings.batting_team}&is_playing_xi=true`).then(({ data }) => {
      setSquadA(Array.isArray(data) ? data.map((s) => ({ player_id: s.player, full_name: s.player_name })) : []);
    });
    client.get(`${ENDPOINTS.SQUADS}?team=${innings.fielding_team}&is_playing_xi=true`).then(({ data }) => {
      setSquadB(Array.isArray(data) ? data.map((s) => ({ player_id: s.player, full_name: s.player_name })) : []);
    });
  }, [innings]);

  useEffect(() => {
    if (!score || score?.is_paused) return;
    if (score?.striker_id) {
      setStriker(prev => score?.striker_id ?? prev);
      setNonStriker(prev => score?.non_striker_id ?? prev);
      setBowler(prev => score?.bowler_id ?? prev);
    }
  }, [score?.striker_id, score?.non_striker_id, score?.bowler_id, score?.is_paused]);

  useEffect(() => {
    if (!score || score?.is_paused) return;
    const ids = score.current_batsmen.map((b) => b.player_id);
    if (striker && !ids.includes(striker)) setStriker('');
    if (nonStriker && !ids.includes(nonStriker)) setNonStriker('');
  }, [score?.current_batsmen, score?.is_paused]);

  if (!match) return <p>Loading...</p>;

  const ballInOver = score?.overs_completed ? Number(score.overs_completed.toString().split('.')[1] || 0) : 0;
  const bowlerLocked = ballInOver > 0 && !!bowler;

  return (
    <div>
      <div className='flex justify-between'>
        <h2 className="text-xl font-semibold mb-4">Scoring Console</h2>
        {!score?.is_paused && score && (
          <Button variant="secondary" onClick={async () => { await client.post(ENDPOINTS.PAUSE_MATCH(matchId)); refetchScore(); }}>⏸ Pause</Button>
        )}
        <Link to="/umpire" className="text-sm text-blue-600 underline self-center">
          <BackButton>Back</BackButton>
        </Link>
      </div>

      {showToss && teamA && teamB && (
        <TossModal match={match} teamA={teamA} teamB={teamB} onClose={() => setShowToss(false)} onDone={() => { refetchMatch(); setKey((k) => k + 1); }} />
      )}
      {score?.is_paused && (
        <div className="bg-amber-50 border border-amber-200 p-4 rounded mb-4 flex items-center justify-between">
          <div className="text-amber-800 text-sm">
            <span className="font-bold">⏸️ Match Paused: </span>
            {score.pause_reason === 'WICKET' ? 'Select the next batsman below, then click Resume.' :
              score.pause_reason === 'INNINGS_END' ? 'Innings Complete. Select the new players below, then click Resume.' :
                'Scoring is paused. Make adjustments below.'}
          </div>
          <Button
            variant="primary"
            onClick={async () => {
              await client.post(ENDPOINTS.RESUME_MATCH(matchId), {
                striker_id: striker,
                non_striker_id: nonStriker,
                bowler_id: bowler
              });
              if (score.pause_reason === 'INNINGS_END') {
                setStriker('');
                setNonStriker('');
                setBowler('');
                if (typeof setKey === 'function') setKey(k => k + 1);
              }
              refetchScore();
            }}
          >
            ▶️ Resume Match
          </Button>
        </div>
      )}
      <LiveScoreWidget matchId={matchId} />
      {innings && (
        <>
          {match.status === 'COMPLETED' ? (
            <MatchResultBox match={match} />
          ) : (
            <>
              <div className="flex flex-col sm:flex-row gap-2 mb-3">
                <select className="border rounded px-2 py-1 text-sm disabled:bg-gray-100 disabled:cursor-not-allowed" value={striker} onChange={(e) => setStriker(e.target.value)}>
                  <option value="">Striker</option>
                  {squadA.filter(p => p.player_id !== nonStriker && !score?.out_player_ids?.includes(p.player_id)).map((p) => <option key={p.player_id} value={p.player_id}>{p.full_name}</option>)}
                </select>
                <select className="border rounded px-2 py-1 text-sm disabled:bg-gray-100 disabled:cursor-not-allowed" value={nonStriker} onChange={(e) => setNonStriker(e.target.value)}>
                  <option value="">Non-striker</option>
                  {squadA.filter(p => p.player_id !== striker && !score?.out_player_ids?.includes(p.player_id)).map((p) => <option key={p.player_id} value={p.player_id}>{p.full_name}</option>)}
                </select>
                <select className="border rounded px-2 py-1 text-sm disabled:bg-gray-100 disabled:cursor-not-allowed" value={bowler} disabled={bowlerLocked}
                  onChange={(e) => setBowler(e.target.value)}>
                  <option value="">Bowler</option>
                  {squadB.map((p) => <option key={p.player_id} value={p.player_id}>{p.full_name}</option>)}
                </select>
              </div>
              {striker && nonStriker && bowler && (
                <BallEntryPad
                  inningsId={innings.innings_id}
                  strikerId={striker}
                  nonStrikerId={nonStriker}
                  bowlerId={bowler}
                  fielders={squadB}
                  onDelivered={() => {
                    setKey((k) => k + 1);
                    refetchScore();
                    refetchMatch();
                  }}
                />
              )}
            </>
          )}
        </>
      )}
    </div>
  );
}