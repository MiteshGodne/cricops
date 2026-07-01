import { useFetch } from '../../../hooks/useFetch';
import { ENDPOINTS } from '../../../api/endpoints';
import { Link } from 'react-router-dom';
import { useAuth } from '../../../context/AuthContext';

export default function MatchCenterListView() {
  const { data, loading } = useFetch(ENDPOINTS.MATCHES);
  const { user } = useAuth();
  const matches = Array.isArray(data) ? data : data?.results || [];

  if (loading) return <p>Loading...</p>;

  return (
    <div>
      <h2 className="text-xl font-semibold mb-4">Matches</h2>
      <div className="grid grid-cols-2 gap-4">
        {matches.map((m) => (
          <div key={m.match_id} className="border p-4 rounded">
            <p className="font-semibold">{m.round_type} R{m.round_number}</p>
            <p className="text-sm text-gray-600">{m.status}</p>
            {user?.role === 'UMPIRE' && m.primary_umpire === user.user_id && m.status !== 'COMPLETED' && (
              <Link to={`/matches/${m.match_id}/score`} className="text-blue-600 text-sm underline">
                Score this match
              </Link>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
