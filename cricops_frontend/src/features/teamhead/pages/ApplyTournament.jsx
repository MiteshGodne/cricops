import { useState } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { useFetch } from '../../../hooks/useFetch';
import { ENDPOINTS } from '../../../api/endpoints';
import { useAuth } from '../../../context/AuthContext';
import client from '../../../api/client';
import Input from '../../../components/Input';
import Button from '../../../components/Button';
import ApplicationStatusBadge from '../../tournaments/components/ApplicationStatusBadge';
import Skeleton from '../../../components/Skeleton';
import toast from 'react-hot-toast';

export default function ApplyTournament() {
  const [searchParams] = useSearchParams();
  const teamId = searchParams.get('team');
  const { user } = useAuth();

  const { data: tournamentsData } = useFetch(ENDPOINTS.TOURNAMENTS);
  const { data: myTeamsData } = useFetch(user ? `${ENDPOINTS.TEAMS}?team_head=${user.user_id}` : null);
  const myTeams = Array.isArray(myTeamsData) ? myTeamsData : myTeamsData?.results || [];
  const myTeamIds = myTeams.map((t) => t.team_id);

  const { data: appsData, refetch } = useFetch(teamId ? `${ENDPOINTS.APPLICATIONS}?team=${teamId}` : null,[teamId]);

  const tournaments = (Array.isArray(tournamentsData) ? tournamentsData : tournamentsData?.results || [])
    .filter((t) => t.status === 'ACCEPTING_APPLICATIONS');
  const myApps = Array.isArray(appsData) ? appsData : appsData?.results || [];

  const { data: allMyAppsData } = useFetch(myTeams.length > 0 ? `${ENDPOINTS.APPLICATIONS}` : null);
  const allApps = (Array.isArray(allMyAppsData) ? allMyAppsData : allMyAppsData?.results || [])
    .filter((a) => myTeamIds.includes(a.team) && ['PENDING','ACCEPTED'].includes(a.status));

  const [form, setForm] = useState({
    tournament: '', registered_name: '', registered_short_name: '',
  });
  const set = (k) => (e) => setForm((p) => ({ ...p, [k]: e.target.value }));

  const alreadyApplied = form.tournament ? allApps.some((a) => a.tournament === form.tournament) : false;

  const apply = async (e) => {
    e.preventDefault();
    if (alreadyApplied) {
      toast.error('You already have a team applied/accepted in this tournament.');
      return;
    }
    try {
      await client.post(ENDPOINTS.SUBMIT_APPLICATION, {
        team_id: teamId,
        tournament_id: form.tournament,
        registered_name: form.registered_name,
        registered_short_name: form.registered_short_name,
      });
      toast.success('Application submitted!');
      setForm({ tournament: '', registered_name: '', registered_short_name: '' });
      refetch();
    } catch (err) {
      toast.error(err.response?.data?.error || JSON.stringify(err.response?.data));
    }
  };

  const reapply = async (appId) => {
    try {
      await client.post(ENDPOINTS.REAPPLY(appId), {});
      toast.success('Reapplied!');
      refetch();
    } catch (err) {
      toast.error(err.response?.data?.error || 'Failed');
    }
  };

  const withdraw = async (appId) => {
    if (!confirm('Withdraw this application?')) return;
    try {
      await client.post(ENDPOINTS.WITHDRAW_APPLICATION(appId), {});
      toast.success('Application withdrawn');
      refetch();
    } catch (err) {
      toast.error(err.response?.data?.error || 'Failed');
    }
  };

  const currentTeam = myTeams.find((t) => t.team_id === teamId);

  return (
    <div className="max-w-2xl mx-auto pb-12">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-bold">Apply to Tournament</h2>
          {currentTeam && (
            <p className="text-sm text-gray-500 mt-1">Team: <strong>{currentTeam.team_name}</strong></p>
          )}
        </div>
        <Link to="/teamhead" className="text-sm text-blue-600 underline">← Back</Link>
      </div>

      <form onSubmit={apply} className="border rounded-xl p-5 mb-6 bg-white shadow-sm">
        <h3 className="font-semibold mb-4">New Application</h3>
        <div className="mb-3">
          <label className="text-sm font-medium block mb-1">Tournament *</label>
          <select className="w-full border rounded px-3 py-2 text-sm"
            value={form.tournament} onChange={set('tournament')} required>
            <option value="">Select open tournament</option>
            {tournaments.map((t) => (
              <option key={t.tournament_id} value={t.tournament_id}>
                {t.name} ({t.category.replace(/_/g,' ')})
              </option>
            ))}
          </select>
          {alreadyApplied && (
            <p className="text-red-500 text-xs mt-1">
              ⚠️ You already have a team applied in this tournament.
            </p>
          )}
        </div>
        <Input label="Register Team As (Display Name) *"
          value={form.registered_name} onChange={set('registered_name')} required />
        <Input label="Short Name (max 10) *"
          value={form.registered_short_name} onChange={set('registered_short_name')}
          maxLength={10} required />
        <Button type="submit" disabled={alreadyApplied}>
          Submit Application
        </Button>
      </form>

      <h3 className="font-semibold mb-3">My Applications</h3>
      {myApps.length === 0 && <p className="text-gray-500 text-sm">No applications for this team yet.</p>}
      <div className="space-y-3">
        {myApps.map((a) => (
          <div key={a.application_id} className="border rounded-xl p-4 bg-white shadow-sm">
            <div className="flex justify-between items-start">
              <div>
                <p className="font-semibold">{a.registered_name}
                  <span className="text-gray-400 text-sm ml-1">({a.registered_short_name})</span>
                </p>
                <p className="text-xs text-gray-400 mt-0.5">Tournament: {a.tournament_name || a.tournament}</p>
                <div className="mt-1"><ApplicationStatusBadge status={a.status} /></div>
                {a.processed_at && (
                  <p className="text-xs text-gray-400 mt-1">
                    Processed: {new Date(a.processed_at).toLocaleDateString()}
                  </p>
                )}
              </div>
              <div className="flex flex-col gap-2">
                {['REJECTED','WITHDRAWN'].includes(a.status) && (
                  <Button variant="secondary" className="text-xs" onClick={() => reapply(a.application_id)}>
                    Reapply
                  </Button>
                )}
                {['PENDING', 'ACCEPTED'].includes(a.status) && (
                  <Button variant="danger" className="text-xs" onClick={() => withdraw(a.application_id)}>
                    Withdraw
                  </Button>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// import { useState } from 'react';
// import { useSearchParams, Link } from 'react-router-dom';
// import { useFetch } from '../../../hooks/useFetch';
// import { ENDPOINTS } from '../../../api/endpoints';
// import client from '../../../api/client';
// import Input from '../../../components/Input';
// import Button from '../../../components/Button';
// import ApplicationStatusBadge from '../../tournaments/components/ApplicationStatusBadge';
// import toast from 'react-hot-toast';

// export default function ApplyTournament() {
//   const [searchParams] = useSearchParams();
//   const teamId = searchParams.get('team');

//   const { data: tournamentsData } = useFetch(ENDPOINTS.TOURNAMENTS);
//   const { data: appsData, refetch } = useFetch(teamId ? `${ENDPOINTS.APPLICATIONS}?team=${teamId}` : null);
//   const tournaments = (Array.isArray(tournamentsData) ? tournamentsData : tournamentsData?.results || [])
//     .filter((t) => t.status === 'ACCEPTING_APPLICATIONS');
//   const myApps = Array.isArray(appsData) ? appsData : appsData?.results || [];

//   const [form, setForm] = useState({ tournament: '', registered_name: '', registered_short_name: '' });
//   const set = (k) => (e) => setForm((p) => ({ ...p, [k]: e.target.value }));

//   const apply = async (e) => {
//     e.preventDefault();
//     try {
//       await client.post(ENDPOINTS.SUBMIT_APPLICATION, {
//         team_id: teamId, tournament_id: form.tournament,
//         registered_name: form.registered_name, registered_short_name: form.registered_short_name,
//       });
//       toast.success('Application submitted!');
//       setForm({ tournament: '', registered_name: '', registered_short_name: '' });
//       refetch();
//     } catch (err) { toast.error(err.response?.data?.error || JSON.stringify(err.response?.data)); }
//   };

//   const reapply = async (appId) => {
//     try {
//       await client.post(ENDPOINTS.REAPPLY(appId), {});
//       toast.success('Reapplied!');
//       refetch();
//     } catch (err) { toast.error(err.response?.data?.error || 'Failed'); }
//   };

//   return (
//     <div className="max-w-2xl mx-auto">
//       <div className="flex items-center justify-between mb-4">
//         <h2 className="text-xl font-bold">Applications</h2>
//         <Link to="/teamhead" className="text-sm text-blue-600 underline">
//          <Button>← Back</Button>
//         </Link>
//       </div>

//       <form onSubmit={apply} className="border rounded p-4 mb-6">
//         <h3 className="font-semibold mb-3">New Application</h3>
//         <div className="mb-3">
//           <label className="text-sm font-medium">Tournament</label>
//           <select className="w-full border rounded px-3 py-2 text-sm mt-1" value={form.tournament} onChange={set('tournament')} required>
//             <option value="">Select open tournament</option>
//             {tournaments.map((t) => <option key={t.tournament_id} value={t.tournament_id}>{t.name} ({t.category})</option>)}
//           </select>
//         </div>
//         <Input label="Register as (Team Name)" value={form.registered_name} onChange={set('registered_name')} required />
//         <Input label="Short Name (max 10)" value={form.registered_short_name} onChange={set('registered_short_name')} maxLength={10} required />
//         <Button type="submit">Submit Application</Button>
//       </form>

//       <h3 className="font-semibold mb-3">My Applications</h3>
//       <div className="space-y-3">
//         {myApps.length === 0 && <p className="text-gray-500">No applications yet.</p>}
//         {myApps.map((a) => (
//           <div key={a.application_id} className="border rounded p-3 flex justify-between items-center">
//               <p className="font-semibold">{a.registered_name}</p>
//               <p className="font-semibold uppercase"> Tournament - {a.tournament_name}</p>
//               <ApplicationStatusBadge status={a.status} />
//             {a.status === 'REJECTED' && (
//               <Button variant="secondary" onClick={() => reapply(a.application_id)}>Reapply</Button>
//             )}
//           </div>
//         ))}
//       </div>
//     </div>
//   );
// }