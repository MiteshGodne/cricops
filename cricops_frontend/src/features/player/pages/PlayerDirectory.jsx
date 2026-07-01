import { useFetch } from '../../../hooks/useFetch';
import { ENDPOINTS } from '../../../api/endpoints';
import PlayerRosterRow from '../components/PlayerRosterRow';

export default function PlayerDirectory() {
  const { data, loading } = useFetch(ENDPOINTS.PLAYERS);
  const players = Array.isArray(data) ? data : data?.results || [];

  if (loading) return <p>Loading...</p>;

  return (
    <div>
      <h2 className="text-xl font-semibold mb-4">Players</h2>
      <table className="w-full text-sm text-left">
        <thead><tr className="border-b font-semibold"><th>Name</th><th>Role</th><th>Nationality</th><th>Status</th></tr></thead>
        <tbody>{players.map((p) => <PlayerRosterRow key={p.player_id} player={p} />)}</tbody>
      </table>
    </div>
  );
}
