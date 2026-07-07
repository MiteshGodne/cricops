import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../../context/AuthContext';
import { useFetch } from '../../../hooks/useFetch';
import { ENDPOINTS } from '../../../api/endpoints';
import client from '../../../api/client';
import Button from '../../../components/Button';
import DeleteButton from '../../../components/DeleteButton';
import Input from '../../../components/Input';
import Skeleton from '../../../components/Skeleton';
import toast from 'react-hot-toast';

const PLAYER_ROLES = ['BATSMAN','BOWLER','ALL_ROUNDER','WICKETKEEPER'];

export default function TeamHeadDashboard() {
  const { user } = useAuth();

  const { data: teamsData, loading: teamsLoading, refetch: refetchTeams } = useFetch(
    user ? `${ENDPOINTS.TEAMS}?team_head=${user.user_id}` : null
  );
  const myTeams = Array.isArray(teamsData) ? teamsData : teamsData?.results || [];

  const [showTeamForm, setShowTeamForm] = useState(false);
  const [teamForm, setTeamForm] = useState({
    team_name: '', short_name: '', city: '', state: '',
    contact_email: '', coach_name: '',
  });
  const [editTeamId, setEditTeamId] = useState(null);
  const [selectedTeam, setSelectedTeam] = useState(null);
  const [showPlayerForm, setShowPlayerForm] = useState(false);
  const [editPlayer, setEditPlayer] = useState(null);
  const [playerForm, setPlayerForm] = useState({
    full_name: '', date_of_birth: '', player_role: 'BATSMAN', nationality: '',
  });

  // Players for selected team — persistent fetch
  const { data: playersData, refetch: refetchPlayers } = useFetch(
    selectedTeam ? `${ENDPOINTS.PLAYERS}?current_team=${selectedTeam.team_id}` : null,
    [selectedTeam?.team_id]
  );
  const players = Array.isArray(playersData) ? playersData : playersData?.results || [];

  const setTF = (k) => (e) => setTeamForm((p) => ({ ...p, [k]: e.target.value }));
  const setPF = (k) => (e) => setPlayerForm((p) => ({ ...p, [k]: e.target.value }));

  const openTeamForm = (t = null) => {
    if (t) {
      setTeamForm({
        team_name: t.team_name, short_name: t.short_name,
        city: t.city, state: t.state,
        contact_email: t.contact_email || '', coach_name: t.coach_name || '',
      });
      setEditTeamId(t.team_id);
    } else {
      setTeamForm({ team_name:'', short_name:'', city:'', state:'', contact_email:'', coach_name:'' });
      setEditTeamId(null);
    }
    setShowTeamForm(true);
  };

  const saveTeam = async (e) => {
    e.preventDefault();
    try {
      if (editTeamId) {
        await client.patch(`${ENDPOINTS.TEAMS}${editTeamId}/`, teamForm);
        toast.success('Team updated');
        if (selectedTeam?.team_id === editTeamId) {
          setSelectedTeam((p) => ({ ...p, ...teamForm }));
        }
      } else {
        await client.post(ENDPOINTS.TEAMS, teamForm);
        toast.success('Team created');
      }
      setShowTeamForm(false);
      setEditTeamId(null);
      refetchTeams();
    } catch (err) { toast.error(JSON.stringify(err.response?.data)); }
  };

  const deleteTeam = async (id) => {
    if (!confirm('Delete team and all its players?')) return;
    try {
      await client.delete(`${ENDPOINTS.TEAMS}${id}/`);
      toast.success('Team deleted');
      if (selectedTeam?.team_id === id) setSelectedTeam(null);
      refetchTeams();
    } catch { toast.error('Cannot delete — team may have active squads'); }
  };

  const savePlayer = async (e) => {
    e.preventDefault();
    try {
      if (editPlayer) {
        await client.patch(`${ENDPOINTS.PLAYERS}${editPlayer.player_id}/`, playerForm);
        toast.success('Player updated');
      } else {
        await client.post(ENDPOINTS.PLAYERS, { ...playerForm, current_team: selectedTeam.team_id });
        toast.success('Player added');
      }
      setShowPlayerForm(false);
      setEditPlayer(null);
      setPlayerForm({ full_name:'', date_of_birth:'', player_role:'BATSMAN', nationality:'' });
      refetchPlayers();
    } catch (err) { toast.error(JSON.stringify(err.response?.data)); }
  };

  const deletePlayer = async (pid) => {
    if (!confirm('Delete player?')) return;
    try {
      await client.delete(`${ENDPOINTS.PLAYERS}${pid}/`);
      toast.success('Player deleted');
      refetchPlayers();
    } catch { toast.error('Cannot delete'); }
  };

  const toggleActivePlayer = async (p) => {
    try {
      await client.patch(`${ENDPOINTS.PLAYERS}${p.player_id}/`, { is_active: !p.is_active });
      toast.success(p.is_active ? 'Player deactivated' : 'Player activated');
      refetchPlayers();
    } catch { toast.error('Failed'); }
  };

  return (
    <div className="max-w-5xl mx-auto pb-12">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-[#183153]">My Dashboard</h2>
        <Button onClick={() => openTeamForm()}>+ New Team</Button>
      </div>

      {/* Team Form */}
      {showTeamForm && (
        <form onSubmit={saveTeam} className="border-2 border-[#183153] rounded-xl p-5 mb-6 bg-white shadow-sm max-w-xl">
          <h3 className="font-semibold mb-4">{editTeamId ? 'Edit Team' : 'Create Team'}</h3>
          <div className="grid grid-cols-2 gap-3">
            <Input label="Team Name *" value={teamForm.team_name} onChange={setTF('team_name')} required />
            <Input label="Short Name (max 10) *" value={teamForm.short_name} onChange={setTF('short_name')} maxLength={10} required />
            <Input label="City *" value={teamForm.city} onChange={setTF('city')} required/>
            <Input label="State *" value={teamForm.state} onChange={setTF('state')} required />
            <Input label="Contact Email" type="email" value={teamForm.contact_email} onChange={setTF('contact_email')} />
            <Input label="Coach Name" value={teamForm.coach_name} onChange={setTF('coach_name')} />
          </div>
          <div className="flex gap-2 mt-4">
            <Button type="submit">Save</Button>
            <Button type="button" variant="secondary" onClick={() => setShowTeamForm(false)}>Cancel</Button>
          </div>
        </form>
      )}

      {teamsLoading ? <Skeleton rows={2} /> : (
        <>
          {myTeams.length === 0 && !showTeamForm && (
            <div className="text-center py-12 text-gray-500">
              <p className="text-lg mb-2">No teams yet</p>
              <Button onClick={() => openTeamForm()}>Create your first team</Button>
            </div>
          )}

          <div className="grid grid-cols-1 gap-4 mb-8">
            {myTeams.map((t) => (
              <div key={t.team_id} className={`border-2 rounded-xl p-5 bg-white shadow-sm transition-all ${
                selectedTeam?.team_id === t.team_id ? 'border-blue-500' : 'border-gray-200'
              }`}>
                <div className="flex justify-between items-start mb-3 capitalize">
                  <div>
                    <h3 className="text-lg font-bold">{t.team_name}</h3>
                    <p className="text-sm text-gray-500">{t.short_name} · {t.city}, {t.state}</p>
                    {t.coach_name && <p className="text-xs text-gray-400">Coach: {t.coach_name}</p>}
                    {t.contact_email && <p className="text-xs text-gray-400">📧 {t.contact_email}</p>}
                  </div>
                  <div className="flex gap-2">
                    <Button variant="secondary" className="text-xs" onClick={() => openTeamForm(t)}>Edit &#9998; </Button>
                    <DeleteButton variant="danger" className="text-xs" onClick={() => deleteTeam(t.team_id)}>Delete</DeleteButton>
                  </div>
                </div>
                <div className="flex flex-wrap gap-2">
                  <Button className="text-xs"
                    onClick={() => setSelectedTeam(selectedTeam?.team_id === t.team_id ? null : t)}>
                    {selectedTeam?.team_id === t.team_id ? '▲ Hide Players' : '👥 Manage Players'}
                  </Button> &rArr; 
                  <SquadLinks team={t} />&rArr;
                  <Link to={`/teamhead/apply?team=${t.team_id}`}>
                    <Button variant="secondary" className="text-xs">🏆 Applications </Button>
                  </Link>
                </div>
              </div>
            ))}
          </div>

          {/* Players Section */}
          {selectedTeam && (
            <div className="border rounded-xl bg-white shadow-sm overflow-hidden">
              <div className="bg-gray-50 px-5 py-4 border-b flex justify-between items-center">
                <h3 className="font-semibold">Players — {selectedTeam.team_name} ({players.length})</h3>
                <Button onClick={() => { setShowPlayerForm(true); setEditPlayer(null); setPlayerForm({ full_name:'', date_of_birth:'', player_role:'BATSMAN', nationality:'' }); }}>
                  + Add Player
                </Button>
              </div>

              {showPlayerForm && (
                <form onSubmit={savePlayer} className="p-5 border-b bg-blue-50">
                  <h4 className="font-semibold mb-3">{editPlayer ? 'Edit Player' : 'New Player'}</h4>
                  <div className="grid grid-cols-2 gap-3 max-w-xl">
                    <Input label="Full Name *" value={playerForm.full_name} onChange={setPF('full_name')} required />
                    <Input label="Date of Birth *" type="date" value={playerForm.date_of_birth} onChange={setPF('date_of_birth')} required />
                    <div>
                      <label className="text-sm font-medium block mb-1">Role *</label>
                      <select className="w-full border rounded px-3 py-2 text-sm"
                        value={playerForm.player_role} onChange={setPF('player_role')}>
                        {PLAYER_ROLES.map((r) => <option key={r}>{r}</option>)}
                      </select>
                    </div>
                    <Input label="Nationality" value={playerForm.nationality} onChange={setPF('nationality')} />
                  </div>
                  <div className="flex gap-2 mt-3">
                    <Button type="submit">Save Player</Button>
                    <Button type="button" variant="secondary" onClick={() => { setShowPlayerForm(false); setEditPlayer(null); }}>Cancel</Button>
                  </div>
                </form>
              )}

              {players.length === 0 ? (
                <p className="p-5 text-gray-500 text-sm">No players yet. Add your first player above.</p>
              ) : (
                <table className="w-full text-sm">
                  <thead className="bg-gray-50 text-xs text-gray-500 uppercase">
                    <tr>
                      <th className="p-3 text-left">Name</th>
                      <th className="p-3 text-left">Role</th>
                      <th className="p-3 text-left">DOB</th>
                      <th className="p-3 text-left">Nationality</th>
                      <th className="p-3 text-center">Status</th>
                      <th className="p-3 text-left">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {players.map((p) => (
                      <tr key={p.player_id} className="border-t hover:bg-gray-50">
                        <td className="p-3 font-medium">{p.full_name}</td>
                        <td className="p-3">
                          <span className={`text-xs px-2 py-0.5 rounded-full ${
                            p.player_role === 'WICKETKEEPER' ? 'bg-purple-100 text-purple-700' :
                            p.player_role === 'BOWLER' ? 'bg-blue-100 text-blue-700' :
                            p.player_role === 'ALL_ROUNDER' ? 'bg-green-100 text-green-700' :
                            'bg-orange-100 text-orange-700'
                          }`}>{p.player_role}</span>
                        </td>
                        <td className="p-3 text-gray-500">{p.date_of_birth}</td>
                        <td className="p-3 text-gray-500">{p.nationality || '—'}</td>
                        <td className="p-3 text-center">
                          <button onClick={() => toggleActivePlayer(p)}
                            className={`text-xs px-2 py-0.5 rounded-full ${p.is_active ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-600'}`}>
                            {p.is_active ? 'Active' : 'Inactive'}
                          </button>
                        </td>
                        <td className="p-3">
                          <div className="flex gap-2">
                            <Button variant='secondary' onClick={() => {
                                setPlayerForm({ full_name: p.full_name, date_of_birth: p.date_of_birth, player_role: p.player_role, nationality: p.nationality });
                                setEditPlayer(p);
                                setShowPlayerForm(true);
                              }}>Edit &#9998;</Button>
                            <DeleteButton variant="danger" className='bg-red-100' onClick={() => deletePlayer(p.player_id)}>Delete</DeleteButton>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
}

function SquadLinks({ team }) {
  const { data } = useFetch(ENDPOINTS.TOURNAMENTS);
  const tournaments = Array.isArray(data) ? data : data?.results || [];
  const [open, setOpen] = useState(false);

  return (
    <div className="relative">
      <Button variant="secondary" className="text-xs" onClick={() => setOpen(!open)}>
        📋 Squad Manager ▾
      </Button>
      {open && (
        <div className="absolute top-full left-0 mt-1 bg-white rounded-lg shadow-lg z-20 min-w-48">
          {tournaments.length === 0 ? (
            <p className="p-3 text-xs text-gray-500">No tournaments found</p>
          ) : (
            tournaments.filter((t)=> !t.status.includes('CANCELLED', 'APPLICATION_CLOSED')).map((t) => (
              <Link key={t.tournament_id}
                to={`/teamhead/teams/${team.team_id}/squad/${t.tournament_id}`}
                className="block px-4 py-2 text-xs hover:bg-gray-50 rounded-lg border-b border-[#efa800] hover:text-[#efa800] last:border-0"
                onClick={() => setOpen(false)}>
                {t.name}
                <span className="text-xs text-gray-400 ml-1">({t.status.replace(/_/g,' ')})</span>
              </Link>
            ))
          )}
        </div>
      )}
    </div>
  );
}