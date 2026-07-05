import { useParams, Link, useNavigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { useFetch } from '../../../hooks/useFetch';
import { ENDPOINTS } from '../../../api/endpoints';
import client from '../../../api/client';
import { useAuth } from '../../../context/AuthContext';
import Button from '../../../components/Button';
import BackButton from '../../../components/BackButton';
import DeleteButton from '../../../components/DeleteButton';
import Input from '../../../components/Input';
import ApplicationStatusBadge from '../../tournaments/components/ApplicationStatusBadge';
import StandingsTable from '../../tournaments/components/StandingsTable';
import Skeleton from '../../../components/Skeleton';
import toast from 'react-hot-toast';
import MatchManage from './MatchManage';

const ROUND_TYPES = ['LEAGUE', 'QUALIFIER', 'QUARTERFINAL', 'SEMIFINAL', 'FINAL'];
const STATUSES = ['UPCOMING', 'ACCEPTING_APPLICATIONS', 'APPLICATIONS_CLOSED', 'ONGOING', 'COMPLETED', 'CANCELLED'];

export default function TournamentManage() {
  const { id } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();
  const [tab, setTab] = useState('applications');

  const { data: tournament } = useFetch(ENDPOINTS.TOURNAMENT_DETAIL(id));
  const { data: appsData, refetch: refetchApps } = useFetch(`${ENDPOINTS.APPLICATIONS}?tournament=${id}`);
  const { data: matchesData, refetch: refetchMatches } = useFetch(`${ENDPOINTS.MATCHES}?tournament=${id}`);
  const { data: groupsData, refetch: refetchGroups } = useFetch(`${ENDPOINTS.GROUPS}?tournament=${id}`);
  const { data: standingsData } = useFetch(`${ENDPOINTS.STANDINGS}?tournament=${id}`);
  const { data: venuesData } = useFetch(ENDPOINTS.VENUES);
  const { data: organizersData, refetch: refetchOrgs } = useFetch(`${ENDPOINTS.ORGANIZERS}?tournament=${id}`);
  const { data: pendingUmpires, error: umpireError } = useFetch(user ? ENDPOINTS.PENDING_UMPIRES : null);
  const { data: teamMatchesAll } = useFetch(`${ENDPOINTS.TEAM_MATCHES}`);

  const apps = Array.isArray(appsData) ? appsData : appsData?.results || [];
  const acceptedApps = apps.filter((a) => a.status === 'ACCEPTED');
  const matches = Array.isArray(matchesData) ? matchesData : matchesData?.results || [];
  const groups = Array.isArray(groupsData) ? groupsData : groupsData?.results || [];
  const standings = Array.isArray(standingsData) ? standingsData : standingsData?.results || [];
  const venues = Array.isArray(venuesData) ? venuesData : venuesData?.results || [];
  const organizers = Array.isArray(organizersData) ? organizersData : organizersData?.results || [];
  const umpires = Array.isArray(pendingUmpires) ? pendingUmpires : pendingUmpires?.results || [];

  const isMyTournament = organizers.some((o) => o.user === user?.user_id);
  useEffect(() => {
    if (organizers.length > 0 && !isMyTournament) {
      toast.error('Not authorized to manage this tournament');
      navigate('/organizer');
    }
  }, [organizers, isMyTournament]);

  const [groupName, setGroupName] = useState('');
  const [matchForm, setMatchForm] = useState({
    venue: '', round_type: 'LEAGUE', round_number: 1, start_date: '', group: '', team_a: '', team_b: '',
  });
  const [assignMatchId, setAssignMatchId] = useState(null);
  const [selectedUmpireId, setSelectedUmpireId] = useState('');
  const [newOrgEmail, setNewOrgEmail] = useState('');
  const [confirmApp, setConfirmApp] = useState(null);

  const setMF = (k) => (e) => setMatchForm((p) => ({ ...p, [k]: e.target.value }));

  const getMatchTeams = (matchId) => {
    const all = Array.isArray(teamMatchesAll) ? teamMatchesAll : teamMatchesAll?.results || [];
    return all.filter((tm) => tm.match === matchId);
  };

  const decide = async (appId, status) => {
    try {
      await client.patch(ENDPOINTS.APPLICATION_DETAIL(appId), { status });
      toast.success(`Application ${status.toLowerCase()}`);
      setConfirmApp(null);
      refetchApps();
    } catch { toast.error('Failed'); }
  };

  const createGroup = async () => {
    if (!groupName.trim()) return;
    try {
      await client.post(ENDPOINTS.GROUPS, { tournament: id, name: groupName });
      toast.success('Group created');
      setGroupName('');
      refetchGroups();
    } catch (err) { toast.error(err.response?.data?.detail || 'Group name may already exist'); }
  };

  const deleteGroup = async (gid) => {
    if (!confirm('Delete group?')) return;
    try {
      await client.delete(ENDPOINTS.GROUP_DETAIL(gid));
      toast.success('Deleted');
      refetchGroups();
    } catch { toast.error('Cannot delete'); }
  };

  const createMatch = async () => {
    if (!matchForm.team_a || !matchForm.team_b) {
      toast.error('Select both teams');
      return;
    }
    if (matchForm.team_a === matchForm.team_b) {
      toast.error('Teams must be different');
      return;
    }
    if (tournament?.start_date && matchForm.start_date) {
      if (new Date(matchForm.start_date) < new Date(tournament.start_date)) {
        toast.error('Match date cannot be before tournament start date');
        return;
      }
    }
    try {
      const { data: newMatch } = await client.post(ENDPOINTS.MATCHES, {
        tournament: tournament?.tournament_id,
        venue: matchForm.venue || null,
        round_type: matchForm.round_type,
        round_number: Number(matchForm.round_number),
        start_date: matchForm.start_date || null,
        ...(matchForm.group && { group: matchForm.group }),
      });
      await Promise.all([
        client.post(ENDPOINTS.TEAM_MATCHES, { match: newMatch.match_id, team: matchForm.team_a, side: 'A' }),
        client.post(ENDPOINTS.TEAM_MATCHES, { match: newMatch.match_id, team: matchForm.team_b, side: 'B' }),
      ]);
      toast.success('Match created');
      setMatchForm({ venue: '', round_type: 'LEAGUE', round_number: 1, start_date: '', group: '', team_a: '', team_b: '' });
      refetchMatches();
    } catch (err) { toast.error(JSON.stringify(err.response?.data)); }
  };

  const deleteMatch = async (mid) => {
    if (!confirm('Delete match?')) return;
    try {
      await client.delete(ENDPOINTS.MATCH_DETAIL(mid));
      toast.success('Match deleted');
      refetchMatches();
    } catch { toast.error('Cannot delete'); }
  };

  const assignUmpire = async (mid) => {
    if (!selectedUmpireId) { toast.error('Select an umpire'); return; }
    const umpire = umpires.find((u) => u.user_id === selectedUmpireId);
    try {
      await client.post(ENDPOINTS.ASSIGN_UMPIRE(mid), { email: umpire.email });
      toast.success(`Umpire ${umpire.email} assigned`);
      setAssignMatchId(null);
      setSelectedUmpireId('');
      refetchMatches();
    } catch (err) { toast.error(err.response?.data?.error || 'Failed'); }
  };

  const addOrganizer = async () => {
    try {
      const { data: usersData } = await client.get(`${ENDPOINTS.USERS}?role=ORGANIZER`);
      const users = Array.isArray(usersData) ? usersData : usersData?.results || [];
      const found = users.find((u) => u.email === newOrgEmail);
      if (!found) { toast.error('Organizer with that email not found, Co-organizers need to be registered.'); return; }
      await client.post(ENDPOINTS.ORGANIZERS, { tournament: id, user: found.user_id });
      toast.success('Co-organizer added');
      setNewOrgEmail('');
      refetchOrgs();
    } catch (err) { toast.error(err.response?.data?.detail || 'Failed'); }
  };

  const updateStatus = async (status) => {
    if (!confirm(`Change status to "${status.replace(/_/g, ' ')}"?`)) return;
    try {
      await client.patch(ENDPOINTS.TOURNAMENT_DETAIL(id), { status });
      toast.success('Status updated');
      window.location.reload();
    } catch { toast.error('Failed'); }
  };

  const TABS = ['applications', 'groups', 'matches', 'standings', 'organizers', 'status update'];

  if (!tournament) return <Skeleton rows={4} />;

  return (
    <div className="max-w-5xl mx-auto pb-12">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold">{tournament.name}</h2>
          <p className="text-sm text-gray-500 mt-1">{tournament.category} ·
            <span className="ml-1 px-2 py-0.5 bg-blue-100 text-blue-700 rounded-full text-xs">{tournament.status}</span>
          </p>
        </div>
        <div className="flex gap-2 items-center">
          <Link to={`/organizer/tournaments/${id}/edit`}>
            <Button variant="secondary">Edit Details &#9998;</Button>
          </Link>
          <Link to="/organizer" className="text-sm text-blue-600 underline self-center"> <BackButton>Back</BackButton></Link>
        </div>
      </div>

      {/* Confirm Application */}
      {confirmApp && (
        <div className="fixed inset-0 bg-white flex items-center justify-center z-50">
          <div className="bg-blue rounded-xl p-6 max-w-sm w-full shadow-xl">
            <h3 className="font-semibold mb-2">Confirm Action</h3>
            <p className="text-sm text-gray-600 mb-4">
              Are you sure you want to <strong>{confirmApp.status}</strong> this application?
            </p>
            <div className="flex gap-3">
              <Button onClick={() => decide(confirmApp.id, confirmApp.status)}>
                Yes, {confirmApp.status}
              </Button>
              <Button variant="secondary" onClick={() => setConfirmApp(null)}>Cancel</Button>
            </div>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="flex gap-1 mb-6 bg-gray-100 p-1 rounded-lg overflow-x-auto">
        {TABS.map((t) => (
          <button key={t} onClick={() => setTab(t)} className={`px-4 py-2 rounded-md text-sm font-medium capitalize whitespace-nowrap transition-all 
            ${tab === t ? 'bg-white shadow text-[#183152]' : 'text-gray-500 hover:text-gray-700'}`}> {t}
          </button>
        ))}
      </div>

      {/* APPLICATIONS */}
      {tab === 'applications' && (
        <div className="space-y-3">
          {apps.length === 0 && <p className="text-gray-500">No applications yet.</p>}
          {apps.map((a) => (
            <div key={a.application_id} className="border rounded-xl p-4 flex justify-between items-center bg-white shadow-sm">
              <div>
                <p className="font-semibold">{a.registered_name}
                  <span className="text-gray-400 text-sm ml-2 uppercase">({a.registered_short_name})</span>
                </p>
                <p className='capitalize'> Team Head - {a.team_head_fname + " " + a.team_head_lname}</p>
              </div>
              <div>
                <div className="mt-1">    <ApplicationStatusBadge status={a.status} /></div>
                {a.processed_by && <p className="text-xs text-gray-400 mt-1"> By: <b> {a.processed_by_name} </b> <br />
                  {a.processed_by_email}</p>}
              </div>
              {a.status === 'PENDING' && (
                <div className="flex gap-2">
                  <Button onClick={() => setConfirmApp({ id: a.application_id, status: 'ACCEPTED' })}>
                    ✓ Accept
                  </Button>
                  <Button variant="danger" onClick={() => setConfirmApp({ id: a.application_id, status: 'REJECTED' })}>
                    ✗ Reject
                  </Button>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* GROUPS */}
      {tab === 'groups' && (
        <div>
          <div className="flex gap-2 mb-4">
            <input className="border rounded-lg px-3 py-2 text-sm flex-1"
              placeholder="Group name (e.g. Group A)"
              value={groupName} onChange={(e) => setGroupName(e.target.value)} />
            <Button onClick={createGroup}>+ Add Group</Button>
          </div>
          <div className="space-y-2">
            {groups.length === 0 && <p className="text-gray-500">No groups yet.</p>}
            {groups.map((g) => (
              <div key={g.group_id} className="border rounded-xl p-4 flex justify-between items-center bg-white shadow-sm">
                <span className="font-medium">{g.name}</span>
                <DeleteButton variant="danger" onClick={() => deleteGroup(g.group_id)}>Delete</DeleteButton>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* MATCHES */}
      {tab === 'matches' && (
        <div>
          <div className="border rounded-xl p-5 mb-6 bg-white shadow-sm">
            <h3 className="font-semibold mb-4">Create Match</h3>
            {acceptedApps.length < 2 ? (
              <p className="text-yellow-600 text-sm">⚠️ Need at least 2 accepted teams to create a match.</p>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium block mb-1">Team A (Side A) *</label>
                  <select className="w-full border rounded px-3 py-2 text-sm" value={matchForm.team_a} onChange={setMF('team_a')}>
                    <option value="">Select Team A</option>
                    {acceptedApps.map((a) => <option key={a.team} value={a.team}>{a.registered_name}</option>)}
                  </select>
                </div>
                <div>
                  <label className="text-sm font-medium block mb-1">Team B (Side B) *</label>
                  <select className="w-full border rounded px-3 py-2 text-sm" value={matchForm.team_b} onChange={setMF('team_b')}>
                    <option value="">Select Team B</option>
                    {acceptedApps.filter((a) => a.team !== matchForm.team_a).map((a) => (
                      <option key={a.team} value={a.team}>{a.registered_name}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="text-sm font-medium block mb-1">Round Type</label>
                  <select className="w-full border rounded px-3 py-2 text-sm" value={matchForm.round_type} onChange={setMF('round_type')}>
                    {ROUND_TYPES.map((r) => <option key={r}>{r}</option>)}
                  </select>
                </div>
                <Input label="Round #" type="number" value={matchForm.round_number} onChange={setMF('round_number')} />
                <div>
                  <label className="text-sm font-medium block mb-1">Group (optional)</label>
                  <select className="w-full border rounded px-3 py-2 text-sm" value={matchForm.group} onChange={setMF('group')}>
                    <option value="">No group</option>
                    {groups.map((g) => <option key={g.group_id} value={g.group_id}>{g.name}</option>)}
                  </select>
                </div>
                <div>
                  <label className="text-sm font-medium block mb-1">Venue</label>
                  <select className="w-full border rounded px-3 py-2 text-sm" value={matchForm.venue} onChange={setMF('venue')} required>
                    <option value="">Select venue</option>
                    {venues.map((v) => <option key={v.venue_id} value={v.venue_id}>{v.name}, {v.city}</option>)}
                  </select>
                </div>
                <div className="sm:col-span-2">
                  <Input label="Match Date & Time" type="datetime-local" value={matchForm.start_date} onChange={setMF('start_date')} />
                </div>
              </div>
            )}
            {acceptedApps.length >= 2 && (<Button className="mt-4" onClick={createMatch}>Create Match</Button>)}
          </div>

          <div className="space-y-3">
            {matches.length === 0 && <p className="text-gray-500">No matches yet.</p>}
            {matches.map((m) => {
              const mTeams = getMatchTeams(m.match_id);
              const tA = mTeams.find((t) => t.side === 'A');
              const tB = mTeams.find((t) => t.side === 'B');
              return (
                <div key={m.match_id} className="border rounded-xl p-4 bg-white shadow-sm">
                  <div className="flex justify-between items-start flex-wrap gap-3">
                    <div>
                      <p className="font-semibold">
                        {tA?.team_name || 'TBD'} <span className="text-gray-400">vs</span> {tB?.team_name || 'TBD'}
                      </p>
                      <p className="text-xs text-gray-500 mt-0.5">
                        {m.round_type} · R{m.round_number}
                        {m.start_date && ` · ${new Date(m.start_date).toLocaleString()}`}
                      </p>
                      <span className={`text-xs px-2 py-0.5 rounded-full mt-1 inline-block ${m.status === 'LIVE' ? 'bg-green-100 text-green-700' :
                        m.status === 'COMPLETED' ? 'bg-gray-100 text-gray-600' : 'bg-blue-100 text-blue-700'
                        }`}>{m.status}</span>
                      <p className="text-xs text-gray-400 mt-1">
                        Umpire: {m.primary_umpire_email || m.primary_umpire || 'Not assigned'}
                      </p>
                    </div>
                    <div className="flex flex-wrap gap-2 items-center">
                      <Link to={`/organizer/matches/${m.match_id}/manage`}>
                        <Button> &#128295; Manage Match</Button>
                      </Link>
                      <Button onClick={() => setAssignMatchId(assignMatchId === m.match_id ? null : m.match_id)}>
                        {m.primary_umpire ? '✓ Reassign Umpire' : 'Assign Umpire'}
                      </Button>
                      <DeleteButton variant="danger" onClick={() => deleteMatch(m.match_id)}>Delete</DeleteButton>
                    </div>
                  </div>
                  {assignMatchId === m.match_id && (
                    <div className="mt-3 p-3 bg-gray-50 rounded-lg">
                      <p className="text-sm font-medium mb-2">Select Umpire (pending applicants)</p>
                      {umpires.length === 0 ? (
                        <p className="text-sm text-gray-500">No pending umpire applicants found.</p>
                      ) : (
                        <div className="flex gap-2">
                          <select className="border rounded px-3 py-2 text-sm flex-1"
                            value={selectedUmpireId}
                            onChange={(e) => setSelectedUmpireId(e.target.value)}>
                            <option value="">Select umpire</option>
                            {umpires.map((u) => (
                              <option key={u.user_id} value={u.user_id}>
                                {u.first_name} {u.last_name} ({u.email})
                              </option>
                            ))}
                          </select>
                          <Button onClick={() => assignUmpire(m.match_id)}>Assign</Button>
                          <Button variant="secondary" onClick={() => setAssignMatchId(null)}>Cancel</Button>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* STANDINGS */}
      {tab === 'standings' && <StandingsTable standings={standings} />}

      {/* ORGANIZERS */}
      {tab === 'organizers' && (
        <div>
          <h3 className="font-semibold mb-3">Tournament Organizers</h3>
          <div className="space-y-2 mb-6">
            {organizers.map((o) => (
              <div key={o.id} className="border rounded-xl p-3 flex justify-between items-center bg-white shadow-sm">
                <div>
                  <p className="font-medium">{o.user_fname + " " + o.user_lname + " [ " + o.user_email + " ]"}</p>
                  {o.is_primary && <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full">Primary</span>}
                </div>
              </div>
            ))}
          </div>
          <div className="border rounded-xl p-4 bg-white shadow-sm">
            <h4 className="font-semibold mb-3">Add Co-Organizer</h4>
            <div className="flex gap-2">
              <input className="border rounded px-3 py-2 text-sm flex-1" placeholder="Organizer email" value={newOrgEmail} onChange={(e) => setNewOrgEmail(e.target.value)} />
              <Button onClick={addOrganizer}> + Add </Button>
            </div>
          </div>
        </div>
      )}

      {/* STATUS UPDATE*/}
      {tab === 'status update' && (
        <div className="border rounded-xl p-5 bg-white shadow-sm">
          <h3 className="font-semibold mb-4">Tournament Status</h3>
          <p className="text-sm text-gray-500 mb-4">Current: <strong>{tournament.status}</strong></p>
          <div className="flex flex-wrap gap-2">
            {STATUSES.map((s) => (
              <button key={s} onClick={() => updateStatus(s)}
                className={`px-4 py-2 rounded-lg text-sm font-medium border transition ${tournament.status === s
                  ? 'bg-[#1b3a65] text-white border-[#1b3a65'
                  : 'hover:bg-gray-50 border-gray-300'
                  }`}>
                {s.replace(/_/g, ' ')}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}