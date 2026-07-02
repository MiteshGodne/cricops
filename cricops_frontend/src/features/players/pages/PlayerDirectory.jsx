import { useFetch } from '../../../hooks/useFetch';
import { ENDPOINTS } from '../../../api/endpoints';
import Skeleton from '../../../components/Skeleton';

export default function PlayerDirectory() {
  const { data, loading } = useFetch(ENDPOINTS.PLAYERS);
  const players = Array.isArray(data) ? data : data?.results || [];

  if (loading) return <Skeleton rows={6} />;

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">All Players</h2>
      <div className="border rounded-xl overflow-hidden shadow-sm">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 text-xs text-gray-500 uppercase">
            <tr>
              <th className="p-3 text-left">Name</th>
              <th className="p-3 text-left">Role</th>
              <th className="p-3 text-left">Team</th>
              <th className="p-3 text-left">Nationality</th>
              <th className="p-3 text-center">Status</th>
            </tr>
          </thead>
          <tbody>
            {players.map((p) => (
              <tr key={p.player_id} className="border-t hover:bg-gray-50">
                <td className="p-3 font-medium">{p.full_name}</td>
                <td className="p-3">
                  <span className={`text-xs px-2 py-0.5 rounded-full ${
                    p.player_role === 'WICKETKEEPER' ? 'bg-purple-100 text-purple-700' :
                    p.player_role === 'BOWLER' ? 'bg-blue-100 text-blue-700' :
                    p.player_role === 'ALL_ROUNDER' ? 'bg-green-100 text-green-700' :
                    'bg-orange-100 text-orange-700'
                  }`}>{p.player_role}</span>
                </td>
                <td className="p-3 text-gray-600">{p.current_team_name || <span className="text-gray-300">—</span>}</td>
                <td className="p-3 text-gray-500">{p.nationality || '—'}</td>
                <td className="p-3 text-center">
                  <span className={`text-xs px-2 py-0.5 rounded-full ${p.is_active ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-500'}`}>
                    {p.is_active ? 'Active' : 'Inactive'}
                  </span>
                </td>
              </tr>
            ))}
            {players.length === 0 && (
              <tr><td colSpan={5} className="p-6 text-center text-gray-400">No players found.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}