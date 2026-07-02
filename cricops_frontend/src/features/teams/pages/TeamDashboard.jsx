import { useState } from 'react';
import { useFetch } from '../../../hooks/useFetch';
import { ENDPOINTS } from '../../../api/endpoints';
import TeamCreationWizard from '../components/TeamCreationWizard';
import { useAuth } from '../../../context/AuthContext';
import { Link } from 'react-router-dom';
import Skeleton from '../../../components/Skeleton';

export default function TeamDashboard() {
  const { user } = useAuth();
  const { data, loading, refetch } = useFetch(ENDPOINTS.TEAMS);
  const teams = Array.isArray(data) ? data : data?.results || [];
  const myTeams = teams.filter((t) => t.team_head === user?.user_id);
  const [showForm, setShowForm] = useState(myTeams.length === 0);

  if (loading) return <Skeleton rows={4} />;

  return (
    <div>
      <h2 className="text-xl font-semibold mb-4">My Teams</h2>
      {myTeams.map((t) => (
        <div key={t.team_id} className="border p-3 rounded mb-2 flex justify-between items-center">
          <span>{t.team_name} ({t.short_name})</span>
        </div>
      ))}
      {showForm
        ? <TeamCreationWizard onCreated={() => { refetch(); setShowForm(false); }} />
        : <button className="text-sm underline" onClick={() => setShowForm(true)}>+ Create another team</button>}
    </div>
  );
}
