import { useParams, Link } from 'react-router-dom';
import { useState } from 'react';
import { useFetch } from '../../../hooks/useFetch';
import { ENDPOINTS } from '../../../api/endpoints';
import { useAuth } from '../../../context/AuthContext';
import StandingsTable from '../components/StandingsTable';
import ApplicationStatusBadge from '../components/ApplicationStatusBadge';
import Skeleton from '../../../components/Skeleton';

const TABS = ['overview', 'regulations', 'teams', 'groups', 'matches', 'standings'];

export default function TournamentDetail() {
  const { id } = useParams();
  const { user } = useAuth();
  const [tab, setTab] = useState('overview');

  const { data: t } = useFetch(`${ENDPOINTS.TOURNAMENTS}${id}/`);
  const { data: regData } = useFetch(t ? `${ENDPOINTS.REGULATIONS}${t.regulation}/` : null, [t?.regulation]);
  const { data: appsData } = useFetch(`${ENDPOINTS.APPLICATIONS}?tournament=${id}`);
  const { data: groupsData } = useFetch(`${ENDPOINTS.GROUPS}?tournament=${id}`);
  const { data: matchesData } = useFetch(`${ENDPOINTS.MATCHES}?tournament=${id}`);
  const { data: standingsData } = useFetch(`${ENDPOINTS.STANDINGS}?tournament=${id}`);

  const apps = (Array.isArray(appsData) ? appsData : appsData?.results || []).filter(a => a.status === 'ACCEPTED');
  const groups = Array.isArray(groupsData) ? groupsData : groupsData?.results || [];
  const matches = Array.isArray(matchesData) ? matchesData : matchesData?.results || [];
  const standings = Array.isArray(standingsData) ? standingsData : standingsData?.results || [];
  const reg = regData;

  if (!t) return <Skeleton rows={5} />;

  const statusColor = {
    UPCOMING: 'bg-blue-100 text-blue-700',
    ACCEPTING_APPLICATIONS: 'bg-green-100 text-green-700',
    APPLICATIONS_CLOSED: 'bg-yellow-100 text-yellow-700',
    ONGOING: 'bg-orange-100 text-orange-700',
    COMPLETED: 'bg-gray-100 text-gray-700',
    CANCELLED: 'bg-red-100 text-red-700',
  };

  return (
    <div className="max-w-5xl mx-auto">
      {/* Hero */}
      <div className="rounded-xl bg-gradient-to-r from-blue-700 to-indigo-800 text-white p-8 mb-6">
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-3xl font-bold mb-2">{t.name}</h1>
            <p className="text-blue-200">{t.category.replace(/_/g, ' ')}</p>
            <div className="flex gap-3 mt-3 flex-wrap">
              <span className={`px-3 py-1 rounded-full text-xs font-semibold ${statusColor[t.status]}`}>{t.status.replace(/_/g, ' ')}</span>
              <span className="text-sm text-blue-100">Start Date 📅 : {t.start_date} → {'TBD'}</span>
              {t.application_deadline && (
                <span className="text-sm text-blue-100">⏰ Apply by {new Date(t.application_deadline).toLocaleDateString()}</span>
              )}
            </div>
          </div>
          {user?.role === 'ORGANIZER' && (
            <Link to={`/organizer/tournaments/${id}/manage`}
              className="bg-white text-blue-700 px-4 py-2 rounded-lg text-sm font-semibold hover:bg-blue-50 transition">
              Manage →
            </Link>
          )}
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 mb-6 bg-gray-100 p-1 rounded-lg overflow-x-auto">
        {TABS.map((tb) => (
          <button key={tb} onClick={() => setTab(tb)}
            className={`px-4 py-2 rounded-md text-sm font-medium capitalize whitespace-nowrap transition-all ${
              tab === tb ? 'bg-white shadow text-blue-700' : 'text-gray-500 hover:text-gray-700'
            }`}>
            {tb}
          </button>
        ))}
      </div>

      {/* OVERVIEW */}
      {tab === 'overview' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <InfoCard title="Tournament Info">
            <Row label="Format" value={reg?.tournament_format?.replace(/_/g,' ')} />
            <Row label="Match Format" value={reg?.match_format} />
            <Row label="Start Date" value={t.start_date} />
            <Row label="Status" value={t.status.replace(/_/g,' ')} />
          </InfoCard>
          <InfoCard title="Application Window">
            <Row label="Opens" value={t.application_starts_from ? new Date(t.application_starts_from).toLocaleString() : 'N/A'} />
            <Row label="Closes" value={t.application_deadline ? new Date(t.application_deadline).toLocaleString() : 'N/A'} />
            <Row label="Teams Registered" value={apps.length} />
          </InfoCard>
          <InfoCard title="Points System">
            <Row label="Win" value={`${reg?.points_for_win} pts`} />
            <Row label="Loss" value={`${reg?.points_for_loss} pts`} />
            <Row label="Tie" value={`${reg?.points_for_tie} pts`} />
            <Row label="No Result" value={`${reg?.points_for_no_result} pts`} />
          </InfoCard>
          <InfoCard title="Match Rules">
            <Row label="Players/Side" value={reg?.players_per_side} />
            <Row label="Overs/Innings" value={reg?.overs_per_innings || 'Unlimited (Test)'} />
            <Row label="Innings/Team" value={reg?.innings_per_team} />
            <Row label="Free Hit" value={reg?.noball_free_hit_enabled ? 'Yes' : 'No'} />
            <Row label="Super Over" value={reg?.super_over_enabled ? 'Yes' : 'No'} />
            <Row label="DRS/Innings" value={reg?.drs_per_innings} />
          </InfoCard>
        </div>
      )}

      {/* REGULATIONS */}
      {tab === 'regulations' && reg && (
        <div className="space-y-4">
          <InfoCard title="Match Regulation">
            <Row label="Match Format" value={reg.match_format} />
            <Row label="Overs/Innings" value={reg.overs_per_innings ?? 'N/A (Test)'} />
            <Row label="Innings/Team" value={reg.innings_per_team} />
            <Row label="Players/Side" value={reg.players_per_side} />
            <Row label="Max Overs/Bowler" value={reg.max_overs_per_bowler ?? 'No limit'} />
            <Row label="Max Bouncers/Over" value={reg.max_bouncers_per_over} />
            <Row label="Wide Value" value={reg.wide_value} />
            <Row label="No Ball Value" value={reg.noball_value} />
            <Row label="Free Hit on No Ball" value={reg.noball_free_hit_enabled ? 'Yes' : 'No'} />
            <Row label="Super Over" value={reg.super_over_enabled ? 'Enabled' : 'Disabled'} />
            <Row label="DRS/Innings" value={reg.drs_per_innings} />
            <Row label="Timed Out (sec)" value={reg.timed_out_limit} />
          </InfoCard>
          <InfoCard title="Tournament Structure">
            <Row label="Format" value={reg.tournament_format.replace(/_/g,' ')} />
            <Row label="Min Teams" value={reg.min_teams} />
            <Row label="Max Teams" value={reg.max_teams ?? 'No limit'} />
            {/* <Row label="Teams/Group" value={reg.teams_per_group ?? 'N/A'} />
            <Row label="Qualify/Group" value={reg.teams_qualifying_per_group ?? 'N/A'} /> */}
          </InfoCard>
          <InfoCard title="Points & Tiebreaker">
            <Row label="Win" value={`${reg.points_for_win} pts`} />
            <Row label="Loss" value={`${reg.points_for_loss} pts`} />
            <Row label="Tie" value={`${reg.points_for_tie} pts`} />
            <Row label="No Result" value={`${reg.points_for_no_result} pts`} />
            <Row label="Forfeit Penalty" value={`${reg.points_penalty_for_forfeit} pts`} />
            <Row label="Over Rate Penalty" value={reg.over_rate_penalty_enabled ? `${reg.over_rate_penalty_points} pts` : 'No'} />
            <Row label="Tiebreaker Order" value={reg.tiebreaker_order?.join(' → ') || 'Default'} />
          </InfoCard>
        </div>
      )}

      {/* TEAMS */}
      {tab === 'teams' && (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {apps.length === 0 && <p className="text-gray-500">No teams accepted yet.</p>}
          {apps.map((a) => (
            <div key={a.application_id} className="border rounded-lg p-4 flex justify-between items-center hover:shadow transition">
              <div>
                <p className="font-semibold">{a.registered_name}</p>
                <p className="text-sm text-gray-500">{a.registered_short_name}</p>
              </div>
              <ApplicationStatusBadge status={a.status} />
            </div>
          ))}
        </div>
      )}

      {/* GROUPS */}
      {tab === 'groups' && (
        <div className="space-y-4">
          {groups.length === 0 && <p className="text-gray-500">No groups defined yet.</p>}
          {groups.map((g) => (
            <GroupCard key={g.group_id} group={g} tournamentId={id} />
          ))}
        </div>
      )}

      {/* MATCHES */}
      {tab === 'matches' && (
        <div className="space-y-3">
          {matches.length === 0 && <p className="text-gray-500">No matches scheduled yet.</p>}
          {matches.map((m) => (<MatchCard key={m.match_id} match={m} />))}
        </div>
      )}

      {/* STANDINGS */}
      {tab === 'standings' && (
        <StandingsTable standings={standings} />
      )}
    </div>
  );
}

function GroupCard({ group, tournamentId }) {
  const { data } = useFetch(`${ENDPOINTS.SQUADS}?tournament=${tournamentId}`);
  const allSquads = Array.isArray(data) ? data : data?.results || [];
  // group doesn't directly filter squads — show group info
  return (
    <div className="border rounded-lg p-4">
      <h3 className="font-semibold text-lg mb-2">{group.name}</h3>
    </div>
  );
}

function MatchCard({ match }) {
  const statusColors = {
    SCHEDULED: 'bg-blue-50 border-blue-200',
    LIVE: 'bg-green-50 border-green-300',
    COMPLETED: 'bg-gray-50 border-gray-200',
    ABANDONED: 'bg-red-50 border-red-200',
  };
  return (
    <div className={`border rounded-lg p-4 ${statusColors[match.status] || ''}`}>
      <div className="flex justify-between items-center">
        <div>
          <span className="text-xs font-semibold text-gray-500 uppercase">{match.round_type} · Round {match.round_number}</span>
          <p className="font-semibold mt-1">{match.team_a || 'TBD'} vs {match.team_b || 'TBD'}</p>
          <p className="text-sm text-gray-500">{match.start_date ? new Date(match.start_date).toLocaleString() : 'Date TBD'}</p>
        </div>
        <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
          match.status === 'LIVE' ? 'bg-green-500 text-white animate-pulse' :
          match.status === 'COMPLETED' ? 'bg-gray-400 text-white' : 'bg-blue-100 text-blue-700'
        }`}>{match.status}</span>
      </div>
    </div>
  );
}

function InfoCard({ title, children }) {
  return (
    <div className="border rounded-xl p-5 bg-white shadow-sm">
      <h3 className="font-semibold text-gray-800 mb-3 pb-2 border-b">{title}</h3>
      <div className="space-y-2">{children}</div>
    </div>
  );
}

function Row({ label, value }) {
  return (
    <div className="flex justify-between text-sm">
      <span className="text-gray-500">{label}</span>
      <span className="font-medium text-gray-800">{value ?? '—'}</span>
    </div>
  );
}