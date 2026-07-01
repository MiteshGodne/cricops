import { useParams } from 'react-router-dom';
import { useState, useEffect } from 'react';
import client from '../../../api/client';
import { ENDPOINTS } from '../../../api/endpoints';
import { useFetch } from '../../../hooks/useFetch';
import LiveScoreWidget from '../components/LiveScoreWidget';
import BallEntryPad from '../components/BallEntryPad';
import TossModal from '../components/TossModal';
import Button from '../../../components/Button';

export default function UmpireScoringConsole() {
  const { matchId } = useParams();
  const { data: match, refetch: refetchMatch } = useFetch(`${ENDPOINTS.MATCHES}${matchId}/`);
  const { data: teamMatchesData } = useFetch(`${ENDPOINTS.TEAM_MATCHES}?match=${matchId}`);
  const teamMatches = Array.isArray(teamMatchesData) ? teamMatchesData : teamMatchesData?.results || [];

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
      setSquadA(Array.isArray(data) ? data.map((s) => s.player_detail || { player_id: s.player, full_name: s.player }) : []);
    });
    client.get(`${ENDPOINTS.SQUADS}?team=${innings.fielding_team}&is_playing_xi=true`).then(({ data }) => {
      setSquadB(Array.isArray(data) ? data.map((s) => s.player_detail || { player_id: s.player, full_name: s.player }) : []);
    });
  }, [innings]);

  if (!match) return <p>Loading...</p>;

  return (
    <div>
      <h2 className="text-xl font-semibold mb-4">Scoring Console</h2>
      {showToss && teamA && teamB && (
        <TossModal match={match} teamA={teamA} teamB={teamB} onClose={() => setShowToss(false)} onDone={() => { refetchMatch(); setKey((k) => k + 1); }} />
      )}
      <LiveScoreWidget matchId={matchId} key={key} />
      {innings && (
        <>
          <div className="flex gap-2 mb-3">
            <select className="border rounded px-2 py-1 text-sm" value={striker} onChange={(e) => setStriker(e.target.value)}>
              <option value="">Striker</option>
              {squadA.map((p) => <option key={p.player_id} value={p.player_id}>{p.full_name}</option>)}
            </select>
            <select className="border rounded px-2 py-1 text-sm" value={nonStriker} onChange={(e) => setNonStriker(e.target.value)}>
              <option value="">Non-striker</option>
              {squadA.map((p) => <option key={p.player_id} value={p.player_id}>{p.full_name}</option>)}
            </select>
            <select className="border rounded px-2 py-1 text-sm" value={bowler} onChange={(e) => setBowler(e.target.value)}>
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
              onDelivered={() => setKey((k) => k + 1)}
            />
          )}
        </>
      )}
    </div>
  );
}
