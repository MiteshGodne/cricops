import { useParams } from 'react-router-dom';
import { useFetch } from '../../../hooks/useFetch';
import { ENDPOINTS } from '../../../api/endpoints';
import { useState } from 'react';
import client from '../../../api/client';
import AddPlayerForm from '../../players/components/AddPlayerForm';
import TournamentSquadGrid from '../components/TournamentSquadGrid';
import Button from '../../../components/Button';
import Skeleton from '../../../components/Skeleton';

export default function ManageSquad() {
  const { teamId, tournamentId } = useParams();
  const { data, loading, refetch } = useFetch(`${ENDPOINTS.SQUADS}?team=${teamId}&tournament=${tournamentId}`);
  const { data: playersData, refetch: refetchPlayers } = useFetch(`${ENDPOINTS.PLAYERS}?current_team=${teamId}`);
  const squad = Array.isArray(data) ? data : data?.results || [];
  const players = Array.isArray(playersData) ? playersData : playersData?.results || [];
  const [jersey, setJersey] = useState('');
  const [selectedPlayer, setSelectedPlayer] = useState('');
  const [error, setError] = useState(null);

  const addToSquad = async () => {
    try {
      await client.post(ENDPOINTS.SQUADS, {
        tournament: tournamentId, team: teamId, player: selectedPlayer, jersey_number: jersey,
      });
      refetch();
      setJersey(''); setSelectedPlayer('');
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to add');
    }
  };

  if (loading) return <Skeleton rows={4} />;

  return (
    <div>
      <h2 className="text-xl font-semibold mb-4">Manage Squad</h2>
      <AddPlayerForm teamId={teamId} onCreated={refetchPlayers} />
      <div className="flex gap-2 items-end mb-4">
        <select className="border rounded px-3 py-2 text-sm" value={selectedPlayer} onChange={(e) => setSelectedPlayer(e.target.value)}>
          <option value="">Select player</option>
          {players.map((p) => <option key={p.player_id} value={p.player_id}>{p.full_name}</option>)}
        </select>
        <input className="border rounded px-3 py-2 text-sm w-24" type="number" placeholder="Jersey #" value={jersey} onChange={(e) => setJersey(e.target.value)} />
        <Button onClick={addToSquad}>+ Add to Squad</Button>
      </div>
      {error && <p className="text-red-500 text-sm">{error}</p>}
      <TournamentSquadGrid squad={squad} />
    </div>
  );
}
