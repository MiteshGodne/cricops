import { useParams, Link } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { useFetch } from '../../../hooks/useFetch';
import { ENDPOINTS } from '../../../api/endpoints';
import client from '../../../api/client';
import Button from '../../../components/Button';
import TossModal from '../../matches/components/TossModal';
import toast from 'react-hot-toast';

export default function MatchManage() {
  const { matchId } = useParams();
  const { data: match, refetch } = useFetch(`${ENDPOINTS.MATCHES}${matchId}/`);
  const { data: tmData, refetch: refetchTM } = useFetch(`${ENDPOINTS.TEAM_MATCHES}?match=${matchId}`);
  const { data: acceptedApps } = useFetch(match ? `${ENDPOINTS.APPLICATIONS}?tournament=${match.tournament}&status=ACCEPTED` : null);

  const teamMatches = Array.isArray(tmData) ? tmData : tmData?.results || [];
  const accepted = Array.isArray(acceptedApps) ? acceptedApps : acceptedApps?.results || [];
  const [showToss, setShowToss] = useState(false);
  const [addTeam, setAddTeam] = useState('');
  const [addSide, setAddSide] = useState('A');

  const addTeamToMatch = async () => {
    try {
      await client.post(ENDPOINTS.TEAM_MATCHES, { match: matchId, team: addTeam, side: addSide });
      toast.success('Team added');
      refetchTM();
    } catch (err) { toast.error(err.response?.data?.error || 'Failed'); }
  };

  const abandon = async () => {
    const reason = prompt('Reason for abandoning?');
    try {
      await client.post(ENDPOINTS.ABANDON_MATCH(matchId), { reason });
      toast.success('Match abandoned');
      refetch();
    } catch { toast.error('Failed'); }
  };

  const teamA = teamMatches.find((t) => t.side === 'A');
  const teamB = teamMatches.find((t) => t.side === 'B');

  if (!match) return <p>Loading...</p>;

  return (
    <div className="max-w-2xl mx-auto">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold">Match Management</h2>
        <Link to={`/organizer/tournaments/${match.tournament}/manage`} className="text-sm text-blue-600 underline">
          <Button>← Back</Button></Link>
      </div>

      <div className="border rounded p-4 mb-4">
        <p><strong>Round:</strong> {match.round_type} R{match.round_number}</p>
        <p><strong>Status:</strong> {match.status}</p>
        <p><strong>Start:</strong> {match.start_date || 'TBD'}</p>
      </div>

      {/* Add teams */}
      <div className="border rounded p-4 mb-4">
        <h3 className="font-semibold mb-3">Teams in Match</h3>
        {teamMatches.map((tm) => (
          <p key={tm.id} className="text-sm mb-1">Side {tm.side}: {tm.team_name || tm.team} {tm.is_toss_winner ? '(Toss Winner)' : ''}</p>
        ))}
        {teamMatches.length < 2 && (
          <div className="flex gap-2 mt-3">
            <select className="border rounded px-3 py-2 text-sm"
              value={addTeam} onChange={(e) => setAddTeam(e.target.value)}>
              <option value="">Select team</option>
              {accepted.map((a) => (
                <option key={a.application_id} value={a.team}>{a.registered_name}</option>
              ))}
            </select>
            <select className="border rounded px-3 py-2 text-sm" value={addSide} onChange={(e) => setAddSide(e.target.value)}>
              <option value="A">Side A</option>
              <option value="B">Side B</option>
            </select>
            <Button onClick={addTeamToMatch}>Add</Button>
          </div>
        )}
      </div>

      {/* Toss */}
      {match.status === 'SCHEDULED' && teamMatches.length === 2 && (
        <Button className="mb-4" onClick={() => setShowToss(true)}>Submit Toss</Button>
      )}
      {showToss && teamA && teamB && (
        <TossModal
          match={match}
          teamA={{ team_id: teamA.team, team_name: teamA.team_name || teamA.team }}
          teamB={{ team_id: teamB.team, team_name: teamB.team_name || teamB.team }}
          onClose={() => setShowToss(false)}
          onDone={refetch}
        />
      )}

      {/* Abandon */}
      {['SCHEDULED', 'LIVE'].includes(match.status) && (
        <Button variant="danger" onClick={abandon}>Abandon Match</Button>
      )}
    </div>
  );
}