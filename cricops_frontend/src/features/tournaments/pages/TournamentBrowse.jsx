import { useFetch } from '../../../hooks/useFetch';
import { ENDPOINTS } from '../../../api/endpoints';
import { Link } from 'react-router-dom';
import { useAuth } from '../../../context/AuthContext';
import Skeleton from '../../../components/Skeleton';
import Button from '../../../components/Button';
import ApplicationStatusBadge from '../components/ApplicationStatusBadge';

export default function TournamentBrowse() {
  const { data, loading } = useFetch(ENDPOINTS.TOURNAMENTS);
  const { user } = useAuth();
  const tournaments = Array.isArray(data) ? data : data?.results || [];

  if (loading) return <Skeleton rows={4} />;

  const statusColor = {
    UPCOMING: 'bg-blue-100 text-blue-700',
    ACCEPTING_APPLICATIONS: 'bg-green-100 text-green-700',
    ONGOING: 'bg-orange-100 text-orange-700',
    COMPLETED: 'bg-gray-100 text-gray-600',
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold">Tournaments</h2>
        {user?.role === 'ORGANIZER' && (
          <Link to="/organizer/tournaments/new"
            className="px-4 py-2 rounded-lg text-sm transition">
            <Button> + New Tournament </Button>
          </Link>
        )}
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {tournaments.map((t) => (
          <Link to={`/tournaments/${t.tournament_id}`} key={t.tournament_id}
            className="border-l-5 border-b-5 border-blue-300 rounded-xl p-5 hover:shadow-md transition-all hover:-translate-y-0.5 group bg-blue-50">
            <div className="flex justify-between items-start mb-3">
              <h3 className="font-semibold text-gray-800 group-hover:text-blue-600 transition">{t.name}</h3>
              <span className={`text-xs px-2 py-1 rounded-full font-medium ${statusColor[t.status] || 'bg-gray-100'}`}>
                {t.status.replace(/_/g, ' ')}
              </span>
            </div>
            <p className="text-sm text-gray-500 mb-2">{t.category.replace(/_/g, ' ')}</p>
            <p className="text-xs text-gray-400">📅 {t.start_date}</p>
            {t.status == 'ACCEPTING_APPLICATION' && (
              <p className="text-xs text-orange-500 mt-1">⏰ Apply by {new Date(t.application_deadline).toLocaleDateString()}</p>
            )}
            {t.status === 'COMPLETED' && (
              <div className="winner-badge pt-2">🏆 Champion: {t.winner_team_name}</div>
            )}
          </Link>
        ))}
        {tournaments.length === 0 && <p className="text-gray-500 col-span-3">No tournaments yet.</p>}
      </div>
    </div>
  );
}