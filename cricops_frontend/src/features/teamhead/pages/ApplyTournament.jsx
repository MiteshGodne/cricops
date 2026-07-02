import { useState } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { useFetch } from '../../../hooks/useFetch';
import { ENDPOINTS } from '../../../api/endpoints';
import client from '../../../api/client';
import Input from '../../../components/Input';
import Button from '../../../components/Button';
import ApplicationStatusBadge from '../../tournaments/components/ApplicationStatusBadge';
import toast from 'react-hot-toast';

export default function ApplyTournament() {
  const [searchParams] = useSearchParams();
  const teamId = searchParams.get('team');

  const { data: tournamentsData } = useFetch(ENDPOINTS.TOURNAMENTS);
  const { data: appsData, refetch } = useFetch(teamId ? `${ENDPOINTS.APPLICATIONS}?team=${teamId}` : null);
  const tournaments = (Array.isArray(tournamentsData) ? tournamentsData : tournamentsData?.results || [])
    .filter((t) => t.status === 'ACCEPTING_APPLICATIONS');
  const myApps = Array.isArray(appsData) ? appsData : appsData?.results || [];

  const [form, setForm] = useState({ tournament: '', registered_name: '', registered_short_name: '' });
  const set = (k) => (e) => setForm((p) => ({ ...p, [k]: e.target.value }));

  const apply = async (e) => {
    e.preventDefault();
    try {
      await client.post(ENDPOINTS.SUBMIT_APPLICATION, {
        team_id: teamId, tournament_id: form.tournament,
        registered_name: form.registered_name, registered_short_name: form.registered_short_name,
      });
      toast.success('Application submitted!');
      setForm({ tournament: '', registered_name: '', registered_short_name: '' });
      refetch();
    } catch (err) { toast.error(err.response?.data?.error || JSON.stringify(err.response?.data)); }
  };

  const reapply = async (appId) => {
    try {
      await client.post(ENDPOINTS.REAPPLY(appId), {});
      toast.success('Reapplied!');
      refetch();
    } catch (err) { toast.error(err.response?.data?.error || 'Failed'); }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold">Applications</h2>
        <Link to="/teamhead" className="text-sm text-blue-600 underline">
         <Button>← Back</Button>
        </Link>
      </div>

      <form onSubmit={apply} className="border rounded p-4 mb-6">
        <h3 className="font-semibold mb-3">New Application</h3>
        <div className="mb-3">
          <label className="text-sm font-medium">Tournament</label>
          <select className="w-full border rounded px-3 py-2 text-sm mt-1" value={form.tournament} onChange={set('tournament')} required>
            <option value="">Select open tournament</option>
            {tournaments.map((t) => <option key={t.tournament_id} value={t.tournament_id}>{t.name} ({t.category})</option>)}
          </select>
        </div>
        <Input label="Register as (Team Name)" value={form.registered_name} onChange={set('registered_name')} required />
        <Input label="Short Name (max 10)" value={form.registered_short_name} onChange={set('registered_short_name')} maxLength={10} required />
        <Button type="submit">Submit Application</Button>
      </form>

      <h3 className="font-semibold mb-3">My Applications</h3>
      <div className="space-y-3">
        {myApps.length === 0 && <p className="text-gray-500">No applications yet.</p>}
        {myApps.map((a) => (
          <div key={a.application_id} className="border rounded p-3 flex justify-between items-center">
              <p className="font-semibold">{a.registered_name}</p>
              <p className="font-semibold uppercase"> Tournament - {a.tournament_name}</p>
              <ApplicationStatusBadge status={a.status} />
            {a.status === 'REJECTED' && (
              <Button variant="secondary" onClick={() => reapply(a.application_id)}>Reapply</Button>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}