import { useParams, Link } from 'react-router-dom';
import { useState } from 'react';
import { useFetch } from '../../../hooks/useFetch';
import { ENDPOINTS } from '../../../api/endpoints';
import client from '../../../api/client';
import Button from '../../../components/Button';
import Skeleton from '../../../components/Skeleton';
import toast from 'react-hot-toast';

export default function ManageSquad() {
  const { teamId, tournamentId } = useParams();
  const { data: squadData, loading, refetch } = useFetch(
    `${ENDPOINTS.SQUADS}?team=${teamId}&tournament=${tournamentId}`
  );
  const { data: playersData } = useFetch(`${ENDPOINTS.PLAYERS}?current_team=${teamId}`);
  const { data: tournamentData } = useFetch(`${ENDPOINTS.TOURNAMENTS}${tournamentId}/`);
  const { data: teamData } = useFetch(`${ENDPOINTS.TEAMS}${teamId}/`);

  const squad = Array.isArray(squadData) ? squadData : squadData?.results || [];
  const players = Array.isArray(playersData) ? playersData : playersData?.results || [];
  const squadPlayerIds = squad.map((s) => s.player);
  const available = players.filter((p) => !squadPlayerIds.includes(p.player_id));

  const [jersey, setJersey] = useState('');
  const [selectedPlayer, setSelectedPlayer] = useState('');
  const [role, setRole] = useState('PLAYER');

  const isAccepting = tournamentData?.status === 'ACCEPTING_APPLICATIONS';

  const addToSquad = async () => {
    if (!isAccepting) {
      toast.error(`Tournament status is "${tournamentData?.status}" — squad entries only allowed during ACCEPTING_APPLICATIONS`);
      return;
    }
    try {
      await client.post(ENDPOINTS.SQUADS, {
        tournament: tournamentId, team: teamId,
        player: selectedPlayer, jersey_number: Number(jersey), squad_role: role,
      });
      toast.success('Added to squad');
      setJersey(''); setSelectedPlayer(''); setRole('PLAYER');
      refetch();
    } catch (err) { toast.error(err.response?.data?.error || 'Failed'); }
  };

  const removeFromSquad = async (squadId) => {
    if (!confirm('Remove from squad?')) return;
    try {
      await client.delete(`${ENDPOINTS.SQUADS}${squadId}/`);
      toast.success('Removed');
      refetch();
    } catch (err) { toast.error(err.response?.data?.error || 'Cannot remove'); }
  };

  if (loading) return <Skeleton rows={4} />;

  return (
    <div className="max-w-3xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-bold">Squad Manager</h2>
          <p className="text-sm text-gray-500 mt-1">
            <span className="font-medium">{teamData?.team_name}</span>
            {' '} → {' '}
            <span className="font-medium">{tournamentData?.name}</span>
            {' '}
            <span className={`text-xs px-2 py-0.5 rounded-full ${isAccepting ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'}`}>
              {tournamentData?.status?.replace(/_/g,' ')}
            </span>
          </p>
        </div>
        <Link to="/teamhead" className="text-sm text-blue-600 underline"><Button>← Back</Button></Link>
      </div>

      {!isAccepting && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 mb-4 text-sm text-yellow-700">
          ⚠️ Tournament is not accepting squad entries. Contact organizer.
        </div>
      )}

      {isAccepting && (
        <div className="border rounded-xl p-5 mb-6 bg-white shadow-sm">
          <h3 className="font-semibold mb-4">Add Player to Squad</h3>
          {available.length === 0 ? (
            <p className="text-sm text-gray-500">All team players are already in this tournament squad.</p>
          ) : (
            <div className="flex flex-wrap gap-3">
              <select className="border rounded px-3 py-2 text-sm flex-1 min-w-48"
                value={selectedPlayer} onChange={(e) => setSelectedPlayer(e.target.value)}>
                <option value="">Select player</option>
                {available.map((p) => (
                  <option key={p.player_id} value={p.player_id}>{p.full_name} ({p.player_role})</option>
                ))}
              </select>
              <input type="number" placeholder="Jersey #" className="border rounded px-3 py-2 text-sm w-28"
                value={jersey} onChange={(e) => setJersey(e.target.value)} />
              <select className="border rounded px-3 py-2 text-sm"
                value={role} onChange={(e) => setRole(e.target.value)}>
                <option value="PLAYER">Player</option>
                <option value="CAPTAIN">Captain</option>
                <option value="VICE_CAPTAIN">Vice Captain</option>
              </select>
              <Button onClick={addToSquad} disabled={!selectedPlayer || !jersey}>Add</Button>
            </div>
          )}
        </div>
      )}

      <div className="border rounded-xl overflow-hidden shadow-sm">
        <div className="bg-gray-50 px-4 py-3 border-b flex justify-between items-center">
          <h3 className="font-semibold">Squad ({squad.length} players)</h3>
        </div>
        {squad.length === 0 ? (
          <p className="text-gray-500 p-4 text-sm">No players in squad yet.</p>
        ) : (
          <table className="w-full text-sm">
            <thead className="bg-gray-50 text-gray-600 text-xs uppercase">
              <tr>
                <th className="p-3 text-left">#</th>
                <th className="p-3 text-left">Player</th>
                <th className="p-3 text-left">Team</th>
                <th className="p-3 text-left">Role</th>
                <th className="p-3 text-left">XI</th>
                <th className="p-3"></th>
              </tr>
            </thead>
            <tbody>
              {squad.map((s) => (
                <tr key={s.squad_id} className="border-t hover:bg-gray-50">
                  <td className="p-3">{s.jersey_number}</td>
                  <td className="p-3 font-medium">{s.player_name || s.player}</td>
                  <td className="p-3 text-gray-500">{s.team_name || s.team}</td>
                  <td className="p-3">
                    <span className={`px-2 py-0.5 rounded-full text-xs ${
                      s.squad_role === 'CAPTAIN' ? 'bg-yellow-100 text-yellow-700' :
                      s.squad_role === 'VICE_CAPTAIN' ? 'bg-blue-100 text-blue-700' :
                      'bg-gray-100 text-gray-600'
                    }`}>{s.squad_role}</span>
                  </td>
                  <td className="p-3">{s.is_playing_xi ? '✓' : '—'}</td>
                  <td className="p-3">
                    <Button variant='danger' onClick={() => removeFromSquad(s.squad_id)}>
                      Remove
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}