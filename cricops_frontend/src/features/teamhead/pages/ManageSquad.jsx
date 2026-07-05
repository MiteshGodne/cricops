import { useParams, Link } from 'react-router-dom';
import { useState } from 'react';
import { useFetch } from '../../../hooks/useFetch';
import { ENDPOINTS } from '../../../api/endpoints';
import { useAuth } from '../../../context/AuthContext';
import client from '../../../api/client';
import DeleteButton from '../../../components/DeleteButton';
import Button from '../../../components/Button';
import BackButton from '../../../components/BackButton';
import Skeleton from '../../../components/Skeleton';
import toast from 'react-hot-toast';

const SQUAD_ROLES = ['PLAYER', 'CAPTAIN', 'VICE_CAPTAIN'];

export default function ManageSquad() {
  const { teamId, tournamentId } = useParams();
  const { user } = useAuth();

  const { data: squadData, loading, refetch } = useFetch(`${ENDPOINTS.SQUADS}?team=${teamId}&tournament=${tournamentId}`, [teamId, tournamentId]);
  const { data: playersData } = useFetch(
    `${ENDPOINTS.PLAYERS}?current_team=${teamId}`,
    [teamId]
  );
  const { data: tournamentData } = useFetch(
    `${ENDPOINTS.TOURNAMENT_DETAIL(tournamentId)}`,
    [tournamentId]
  );
  const { data: teamData } = useFetch(
    `${ENDPOINTS.TEAM_DETAIL(teamId)}`,
    [teamId]
  );

  const squad = Array.isArray(squadData) ? squadData : squadData?.results || [];
  const players = Array.isArray(playersData) ? playersData : playersData?.results || [];

  const isOwner = teamData?.team_head === user?.user_id;

  const squadPlayerIds = squad.map((s) => s.player);
  const available = players.filter((p) => !squadPlayerIds.includes(p.player_id));

  const [jersey, setJersey] = useState('');
  const [selectedPlayer, setSelectedPlayer] = useState('');
  const [role, setRole] = useState('PLAYER');

  const [editSquadId, setEditSquadId] = useState(null);
  const [editRole, setEditRole] = useState('PLAYER');
  const [editJersey, setEditJersey] = useState('');
  const [editIsXI, setEditIsXI] = useState(true);

  const isAccepting = tournamentData?.status === 'ACCEPTING_APPLICATIONS';

  const hasCaptain = squad.some((s) => s.squad_role === 'CAPTAIN');

  const addToSquad = async () => {
    if (!isOwner) { toast.error('You do not own this team.'); return; }
    if (!isAccepting) {
      toast.error(`Tournament is "${tournamentData?.status}" — squad changes not allowed now.`);
      return;
    }
    if (role === 'CAPTAIN' && hasCaptain) {
      toast.error('A captain is already assigned. Remove existing captain first.');
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
    } catch (err) {
      toast.error(err.response?.data?.error || JSON.stringify(err.response?.data));
    }
  };

  const removeFromSquad = async (squadId) => {
    if (!isOwner) { toast.error('You do not own this team.'); return; }
    if (!confirm('Remove from squad?')) return;
    try {
      await client.delete(`${ENDPOINTS.SQUADS}${squadId}/`);
      toast.success('Removed from squad');
      refetch();
    } catch (err) {
      toast.error(err.response?.data?.error || 'Cannot remove');
    }
  };

  const startEdit = (s) => {
    setEditSquadId(s.squad_id);
    setEditRole(s.squad_role);
    setEditJersey(s.jersey_number);
    setEditIsXI(s.is_playing_xi);
  };

  const saveEdit = async (squadId) => {
    if (!isOwner) { toast.error('You do not own this team.'); return; }
    if (editRole === 'CAPTAIN') {
      const existingCaptain = squad.find((s) => s.squad_role === 'CAPTAIN' && s.squad_id !== squadId);
      if (existingCaptain) {
        toast.error('A captain already exists. Remove existing captain first.');
        return;
      }
    }
    try {
      await client.patch(`${ENDPOINTS.SQUADS}${squadId}/`, {
        squad_role: editRole,
        jersey_number: Number(editJersey),
        is_playing_xi: editIsXI,
      });
      toast.success('Updated');
      setEditSquadId(null);
      refetch();
    } catch (err) {
      toast.error(err.response?.data?.error || 'Failed');
    }
  };

  if (loading) return <Skeleton rows={4} />;

  if (!isOwner) {
    return (
      <div className="text-center py-12">
        <p className="text-red-500">You do not have permission to manage this squad.</p>
        <Link to="/teamhead" className="text-blue-600 underline text-sm mt-2 block">
          <BackButton>Back</BackButton>
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto pb-12">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-bold">Squad Manager</h2>
          <p className="text-sm text-gray-500 mt-1">
            <span className="font-medium">{teamData?.team_name}</span>
            <span className="mx-2 text-gray-300">→</span>
            <span className="font-medium">{tournamentData?.name}</span>
            <span className={`ml-2 text-xs px-2 py-0.5 rounded-full ${isAccepting ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'
              }`}>
              {tournamentData?.status?.replace(/_/g, ' ')}
            </span>
          </p>
        </div>
        <Link to="/teamhead" className="text-sm text-blue-600 underline">
          <BackButton>Back</BackButton>
        </Link>
      </div>

      {!isAccepting && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 mb-4 text-sm text-yellow-700">
          ⚠️ Squad changes only allowed when tournament is ACCEPTING_APPLICATIONS.
        </div>
      )}

      {/* Add player */}
      {isAccepting && (
        <div className="border rounded-xl p-5 mb-6 bg-white shadow-sm">
          <h3 className="font-semibold mb-3">Add Player to Squad</h3>
          {available.length === 0 ? (
            <p className="text-sm text-gray-500">
              All team players are already in this tournament squad, or you need to add players to the team first.
            </p>
          ) : (
            <div className="flex flex-wrap gap-3 items-end">
              <div className="flex-1 min-w-48">
                <label className="text-xs font-medium text-gray-500 block mb-1">Player</label>
                <select className="w-full border rounded px-3 py-2 text-sm"
                  value={selectedPlayer} onChange={(e) => setSelectedPlayer(e.target.value)}>
                  <option value="">Select player</option>
                  {available.map((p) => (
                    <option key={p.player_id} value={p.player_id}>
                      {p.full_name.upper()} ({p.player_role})
                    </option>
                  ))}
                </select>
              </div>
              <div className="w-28">
                <label className="text-xs font-medium text-gray-500 block mb-1">Jersey #</label>
                <input type="number" className="w-full border rounded px-3 py-2 text-sm"
                  value={jersey} onChange={(e) => setJersey(e.target.value)} placeholder="e.g. 7" />
              </div>
              <div>
                <label className="text-xs font-medium text-gray-500 block mb-1">Role</label>
                <select className="border rounded px-3 py-2 text-sm"
                  value={role} onChange={(e) => setRole(e.target.value)}>
                  {SQUAD_ROLES.map((r) => (
                    <option key={r} value={r} disabled={r === 'CAPTAIN' && hasCaptain}>
                      {r}{r === 'CAPTAIN' && hasCaptain ? ' (taken)' : ''}
                    </option>
                  ))}
                </select>
              </div>
              <Button onClick={addToSquad} disabled={!selectedPlayer || !jersey}>+ Add</Button>
            </div>
          )}
        </div>
      )}

      {/* Squad table */}
      <div className="border rounded-xl overflow-hidden shadow-sm bg-white">
        <div className="bg-gray-50 px-5 py-3 border-b">
          <h3 className="font-semibold">Current Squad ({squad.length} players)</h3>
        </div>
        {squad.length === 0 ? (
          <p className="p-6 text-gray-400 text-sm text-center">No players in squad yet.</p>
        ) : (
          <table className="w-full text-sm">
            <thead className="bg-gray-50 text-xs text-gray-500 uppercase">
              <tr>
                <th className="p-3 text-left">#</th>
                <th className="p-3 text-left">Player</th>
                <th className="p-3 text-left">Role</th>
                <th className="p-3 text-center">WK</th>
                <th className="p-3 text-center">XI</th>
                <th className="p-3 text-left">Actions</th>
              </tr>
            </thead>
            <tbody>
              {squad.map((s) => (
                <tr key={s.squad_id} className="border-t hover:bg-gray-50">
                  {editSquadId === s.squad_id ? (
                    <>
                      <td className="p-3">
                        <input type="number" className="border rounded px-2 py-1 text-sm w-16"
                          value={editJersey} onChange={(e) => setEditJersey(e.target.value)} />
                      </td>
                      <td className="p-3 font-medium">{s.player_name || s.player}</td>
                      <td className="p-3">
                        <select className="border rounded px-2 py-1 text-sm"
                          value={editRole} onChange={(e) => setEditRole(e.target.value)}>
                          {SQUAD_ROLES.map((r) => <option key={r}>{r}</option>)}
                        </select>
                      </td>
                      <td className="p-3 text-center">{s.is_wicketkeeper ? '✓' : '—'}</td>
                      <td className="p-3 text-center">
                        <input type="checkbox" checked={editIsXI} onChange={(e) => setEditIsXI(e.target.checked)} />
                      </td>
                      <td className="p-3">
                        <div className="flex gap-2">
                          <button className="text-green-600 text-xs hover:underline font-medium"
                            onClick={() => saveEdit(s.squad_id)}>Save</button>
                          <button className="text-gray-500 text-xs hover:underline"
                            onClick={() => setEditSquadId(null)}>Cancel</button>
                        </div>
                      </td>
                    </>
                  ) : (
                    <>
                      <td className="p-3 font-medium">{s.jersey_number}</td>
                      <td className="p-3 font-medium">{s.player_name || s.player}</td>
                      <td className="p-3">
                        <span className={`text-xs px-2 py-0.5 rounded-full ${s.squad_role === 'CAPTAIN' ? 'bg-yellow-100 text-yellow-700' :
                            s.squad_role === 'VICE_CAPTAIN' ? 'bg-blue-100 text-blue-700' :
                              'bg-gray-100 text-gray-600'
                          }`}>{s.squad_role}</span>
                      </td>
                      <td className="p-3 text-center">{s.is_wicketkeeper ? '🧤' : '—'}</td>
                      <td className="p-3 text-center">{s.is_playing_xi ? '✓' : '—'}</td>
                      <td className="p-3">
                        <div className="flex gap-2">
                          {isAccepting && (
                            <>
                              <Button className="text-blue-600 text-xs hover:underline"
                                onClick={() => startEdit(s)}>Edit &#9998;  </Button>
                              <DeleteButton className="text-red-500 text-xs hover:underline"
                                onClick={() => removeFromSquad(s.squad_id)}>Remove</DeleteButton>
                            </>
                          )}
                        </div>
                      </td>
                    </>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}