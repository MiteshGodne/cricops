import { useParams } from 'react-router-dom';
import { useFetch } from '../../../hooks/useFetch';
import { ENDPOINTS } from '../../../api/endpoints';
import StandingsTable from '../components/StandingsTable';
import ApplicationStatusBadge from '../components/ApplicationStatusBadge';
import client from '../../../api/client';

export default function TournamentControlPanel() {
  const { id } = useParams();
  const { data: tData } = useFetch(`${ENDPOINTS.TOURNAMENTS}${id}/`);
  const { data: appsData, refetch: refetchApps } = useFetch(`${ENDPOINTS.APPLICATIONS}?tournament=${id}`);
  const { data: standingsData } = useFetch(`${ENDPOINTS.STANDINGS}?tournament=${id}`);

  const apps = Array.isArray(appsData) ? appsData : appsData?.results || [];
  const standings = Array.isArray(standingsData) ? standingsData : standingsData?.results || [];

  const decide = async (appId, status) => {
    await client.patch(`${ENDPOINTS.APPLICATIONS}${appId}/`, { status });
    refetchApps();
  };

  return (
    <div>
      <h2 className="text-xl font-semibold mb-4">{tData?.name}</h2>

      <h3 className="font-semibold mt-6 mb-2">Applications</h3>
      {apps.map((a) => (
        <div key={a.application_id} className="border p-3 rounded mb-2 flex justify-between items-center">
          <span>{a.registered_name} ({a.registered_short_name})</span>
          <ApplicationStatusBadge status={a.status} />
          {a.status === 'PENDING' && (
            <div className="flex gap-2">
              <button className="text-green-600 text-sm" onClick={() => decide(a.application_id, 'ACCEPTED')}>Accept</button>
              <button className="text-red-600 text-sm" onClick={() => decide(a.application_id, 'REJECTED')}>Reject</button>
            </div>
          )}
        </div>
      ))}

      <h3 className="font-semibold mt-6 mb-2">Standings</h3>
      <StandingsTable standings={standings} />
    </div>
  );
}
