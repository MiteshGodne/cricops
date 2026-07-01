import { useFetch } from '../../../hooks/useFetch';
import { ENDPOINTS } from '../../../api/endpoints';
import { Link } from 'react-router-dom';

export default function TournamentBrowse() {
  const { data, loading } = useFetch(ENDPOINTS.TOURNAMENTS);
  const tournaments = Array.isArray(data) ? data : data?.results || [];

  if (loading) return <p>Loading...</p>;

  return (
    <div>
      <h2 className="text-xl font-semibold mb-4">Tournaments</h2>
      <div className="grid grid-cols-2 gap-4">
        {tournaments.map((t) => (
          <div key={t.tournament_id} className="border p-4 rounded">
            <h3 className="font-semibold">{t.name}</h3>
            <p className="text-sm text-gray-600">{t.category} · {t.status}</p>
            <p className="text-xs text-gray-500">{t.start_date} → {t.end_date}</p>
            <Link to={`/tournaments/${t.tournament_id}/manage`} className="text-blue-600 text-sm underline">
              Manage
            </Link>
          </div>
        ))}
      </div>
    </div>
  );
}
