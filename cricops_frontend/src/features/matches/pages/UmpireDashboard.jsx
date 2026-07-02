import { useAuth } from '../../../context/AuthContext';
import { useFetch } from '../../../hooks/useFetch';
import { ENDPOINTS } from '../../../api/endpoints';
import { Link } from 'react-router-dom';
import Button from '../../../components/Button';
import Skeleton from '../../../components/Skeleton';

export default function UmpireDashboard() {
  const { user } = useAuth();
  const { data, loading } = useFetch(ENDPOINTS.MATCHES);
  const matches = (Array.isArray(data) ? data : data?.results || [])
    .filter((m) => m.primary_umpire === user?.user_id);

  if (loading) return <Skeleton rows={3} />;

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">Umpire Dashboard</h2>
      {matches.length === 0 && <p className="text-gray-500">No matches assigned to you yet.</p>}
      <div className="space-y-3">
        {matches.map((m) => (
          <div key={m.match_id} className="border rounded p-4 flex justify-between items-center">
            <div>
              <p className="font-semibold">{m.round_type} R{m.round_number}</p>
              <p className="text-sm text-gray-500">Status: {m.status}</p>
              <p className="text-xs text-gray-400">{m.start_date || 'Date TBD'}</p>
            </div>
            {m.status === 'LIVE' && (
              <Link to={`/matches/${m.match_id}/score`}>
                <Button>Score Now</Button>
              </Link>
            )}
            {m.status === 'SCHEDULED' && (
              <span className="text-sm text-yellow-600">Waiting for toss</span>
            )}
            {m.status === 'COMPLETED' && (
              <span className="text-sm text-green-600">Completed</span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}