import { Link } from 'react-router-dom';
import { useFetch } from '../../../hooks/useFetch';
import { ENDPOINTS } from '../../../api/endpoints';
import { useAuth } from '../../../context/AuthContext';
import Button from '../../../components/Button';
import Skeleton from '../../../components/Skeleton';
import client from '../../../api/client';
import toast from 'react-hot-toast';

export default function OrganizerDashboard() {
  const { user } = useAuth();
  const { data, loading, refetch } = useFetch(ENDPOINTS.TOURNAMENTS);
  const tournaments = (Array.isArray(data) ? data : data?.results || [])
    .filter((t) => t.created_by === user?.user_id);

  const deleteTournament = async (id) => {
    if (!confirm('Delete this tournament?')) return;
    try {
      await client.delete(`${ENDPOINTS.TOURNAMENTS}${id}/`);
      toast.success('Deleted');
      refetch();
    } catch {
      toast.error('Cannot delete — has matches or applications');
    }
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold">Organizer Dashboard</h2>
        <Link to="/organizer/tournaments/new">
          <Button>+ New Tournament</Button>
        </Link>
      </div>

      <h3 className="font-semibold mb-3">My Tournaments</h3>
      {loading ? <Skeleton rows={3} /> : (
        <div className="space-y-3">
          {tournaments.length === 0 && <p className="text-gray-500">No tournaments yet.</p>}
          {tournaments.map((t) => (
            <div key={t.tournament_id} className="border rounded p-4 flex justify-between items-center">
              <div>
                <p className="font-semibold">{t.name}</p>
                <p className="text-sm text-gray-600">Category : {t.category} · {t.status}</p>
                <p className="text-xs text-gray-600">📅Start Date : {t.start_date} → {'TBD'}</p>
              </div>
              <div className="flex gap-2">
                <Link to={`/organizer/tournaments/${t.tournament_id}/manage`}>
                  <Button variant="secondary">Manage</Button>
                </Link>
                <Link to={`/organizer/tournaments/${t.tournament_id}/edit`}>
                  <Button variant="secondary">Edit</Button>
                </Link>
                <Button variant="danger" onClick={() => deleteTournament(t.tournament_id)}>Delete</Button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}