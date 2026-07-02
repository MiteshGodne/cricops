import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import client from '../../../api/client';
import { ENDPOINTS } from '../../../api/endpoints';
import Input from '../../../components/Input';
import Button from '../../../components/Button';
import toast from 'react-hot-toast';

const CATEGORIES = ['INTER_COLLEGE','INTER_SCHOOL','CLUB_LEVEL','DISTRICT_LEVEL','STATE_LEVEL','NATIONAL_LEVEL','CORPORATE_LEVEL','OPEN'];
const FORMATS = ['T20','ODI','T10','CUSTOM','TEST'];
const T_FORMATS = ['LEAGUE','KNOCKOUT','GROUP_KNOCKOUT','DOUBLE_ELIMINATION'];
const TIEBREAKERS = ['NRR','H2H','BOWL_OUT','SUPER_OVER','MOST_WINS'];

export default function TournamentForm() {
  const { id } = useParams();
  const navigate = useNavigate();
  const isEdit = Boolean(id);

  const [reg, setReg] = useState({
    match_format: 'T20', overs_per_innings: 20, innings_per_team: 1,
    players_per_side: 11, max_overs_per_bowler: 4, max_bouncers_per_over: 1,
    wide_value: 1, noball_value: 1, noball_free_hit_enabled: true,
    super_over_enabled: false, drs_per_innings: 2, timed_out_limit: 180,
    tournament_format: 'LEAGUE', min_teams: 2, max_teams: '',
    teams_per_group: '', teams_qualifying_per_group: '',
    points_for_win: 2, points_for_tie: 1, points_for_loss: 0,
    points_for_no_result: 1, points_penalty_for_forfeit: 0,
    over_rate_penalty_enabled: false, over_rate_penalty_points: 0,
    tiebreaker_order: [],
  });
  const [form, setForm] = useState({
    name: '', category: 'OPEN',
    start_date: '', application_starts_from: '', application_deadline: '',
  });
  const [regId, setRegId] = useState(null);
  const [existingTournamentStatus, setExistingTournamentStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});

  useEffect(() => {
    if (!isEdit) return;
    client.get(`${ENDPOINTS.TOURNAMENTS}${id}/`).then(({ data }) => {
      setForm({
        name: data.name, category: data.category,
        start_date: data.start_date,
        application_starts_from: data.application_starts_from?.slice(0,16) || '',
        application_deadline: data.application_deadline?.slice(0,16) || '',
      });
      setRegId(data.regulation);
      setExistingTournamentStatus(data.status);
      client.get(`${ENDPOINTS.REGULATIONS}${data.regulation}/`).then(({ data: r }) => setReg({...reg, ...r}));
    });
  }, [id]);

  const setR = (k) => (e) => {
    const v = e.target.type === 'checkbox' ? e.target.checked : e.target.value;
    setReg((p) => ({ ...p, [k]: v }));
  };
  const setF = (k) => (e) => setForm((p) => ({ ...p, [k]: e.target.value }));

  const validate = () => {
    const e = {};
    if (!form.name) e.name = 'Required';
    if (!form.start_date) e.start_date = 'Required';
    if (form.application_starts_from && form.application_deadline) {
      if (new Date(form.application_starts_from) >= new Date(form.application_deadline))
        e.application_deadline = 'Close date must be after open date';
    }
    if (form.application_starts_from && form.start_date) {
      if (new Date(form.application_starts_from) < new Date(form.start_date)) {
        // allow before start date — teams need to register before tournament begins
      }
    }
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const canEditReg = !isEdit || !['ONGOING','COMPLETED'].includes(existingTournamentStatus);

  const submit = async (e) => {
    e.preventDefault();
    if (!validate()) return;
    setLoading(true);
    try {
      let regulationId = regId;
      if (!isEdit) {
        const regPayload = { ...reg };
        if (!regPayload.overs_per_innings || reg.match_format === 'TEST') delete regPayload.overs_per_innings;
        if (regPayload.tournament_format !== 'GROUP_KNOCKOUT') {
          regPayload.teams_per_group = null;
          regPayload.teams_qualifying_per_group = null;
        } else {
          regPayload.teams_per_group = regPayload.teams_per_group === '' ? null : parseInt(regPayload.teams_per_group, 10);
          regPayload.teams_qualifying_per_group = regPayload.teams_qualifying_per_group === '' ? null : parseInt(regPayload.teams_qualifying_per_group, 10);
        }
        if (regPayload.max_teams === '') regPayload.max_teams = null;
        const { data: rd } = await client.post(ENDPOINTS.REGULATIONS, regPayload);
        regulationId = rd.regulation_id;
      } else if (canEditReg) {
        const regPayload = { ...reg };
        if (regPayload.tournament_format !== 'GROUP_KNOCKOUT') {
          regPayload.teams_per_group = null;
          regPayload.teams_qualifying_per_group = null;
        } else {
          regPayload.teams_per_group = regPayload.teams_per_group === '' ? null : parseInt(regPayload.teams_per_group, 10);
          regPayload.teams_qualifying_per_group = regPayload.teams_qualifying_per_group === '' ? null : parseInt(regPayload.teams_qualifying_per_group, 10);
        }
        if (regPayload.max_teams === '') regPayload.max_teams = null;
        await client.patch(`${ENDPOINTS.REGULATIONS}${regId}/`, reg);
      }
      const payload = { ...form, regulation: regulationId };
      if (isEdit) {
        await client.patch(`${ENDPOINTS.TOURNAMENTS}${id}/`, payload);
        toast.success('Tournament updated');
      } else {
        await client.post(ENDPOINTS.TOURNAMENTS, payload);
        toast.success('Tournament created!');
      }
      navigate('/organizer');
    } catch (err) {
      toast.error(JSON.stringify(err.response?.data));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto mt-6 pb-12">
      <h2 className="text-2xl font-bold mb-6">{isEdit ? 'Edit Tournament' : 'Create Tournament'}</h2>
      <form onSubmit={submit} className="space-y-6">

        {/* TOURNAMENT BASICS */}
        <Section title="Tournament Details">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="sm:col-span-2">
              <Input label="Tournament Name *" value={form.name} onChange={setF('name')} error={errors.name} required />
            </div>
            <div>
              <label className="text-sm font-medium block mb-1">Category *</label>
              <select className="w-full border rounded px-3 py-2 text-sm" value={form.category} onChange={setF('category')}>
                {CATEGORIES.map((c) => <option key={c}>{c.replace(/_/g,' ')}</option>)}
              </select>
            </div>
            <Input label="Start Date *" type="date" value={form.start_date} onChange={setF('start_date')} error={errors.start_date} required />
            <Input label="Application Opens" type="datetime-local" value={form.application_starts_from} onChange={setF('application_starts_from')} />
            <Input label="Application Deadline" type="datetime-local" value={form.application_deadline} onChange={setF('application_deadline')} error={errors.application_deadline} />
          </div>
          <p className="text-xs text-gray-400 mt-2">ℹ️ Status defaults to UPCOMING. You can change it from the manage panel.</p>
        </Section>

        {/* REGULATION */}
        {(!isEdit || canEditReg) && (
          <>
            <Section title="Match Rules">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium block mb-1">Match Format *</label>
                  <select className="w-full border rounded px-3 py-2 text-sm" value={reg.match_format} onChange={setR('match_format')}>
                    {FORMATS.map((f) => <option key={f}>{f}</option>)}
                  </select>
                </div>
                {reg.match_format !== 'TEST' && (
                  <Input label="Overs/Innings *" type="number" value={reg.overs_per_innings} onChange={setR('overs_per_innings')} min={1} />
                )}
                <Input label="Innings/Team" type="number" value={reg.innings_per_team} onChange={setR('innings_per_team')} min={1} />
                <Input label="Players/Side" type="number" value={reg.players_per_side} onChange={setR('players_per_side')} min={1} max={15} />
                <Input label="Max Overs/Bowler" type="number" value={reg.max_overs_per_bowler} onChange={setR('max_overs_per_bowler')} />
                <Input label="Max Bouncers/Over" type="number" value={reg.max_bouncers_per_over} onChange={setR('max_bouncers_per_over')} />
                <Input label="Wide Value (runs)" type="number" value={reg.wide_value} onChange={setR('wide_value')} />
                <Input label="No Ball Value (runs)" type="number" value={reg.noball_value} onChange={setR('noball_value')} />
                <Input label="DRS/Innings" type="number" value={reg.drs_per_innings} onChange={setR('drs_per_innings')} />
                <Input label="Timed Out Limit (sec)" type="number" value={reg.timed_out_limit} onChange={setR('timed_out_limit')} />
                <CheckRow label="Free Hit on No Ball" checked={reg.noball_free_hit_enabled} onChange={setR('noball_free_hit_enabled')} />
                <CheckRow label="Super Over Enabled" checked={reg.super_over_enabled} onChange={setR('super_over_enabled')} />
                <CheckRow label="Over Rate Penalty" checked={reg.over_rate_penalty_enabled} onChange={setR('over_rate_penalty_enabled')} />
                {reg.over_rate_penalty_enabled && (
                  <Input label="Penalty Points" type="number" value={reg.over_rate_penalty_points} onChange={setR('over_rate_penalty_points')} />
                )}
              </div>
            </Section>

            <Section title="Tournament Structure">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium block mb-1">Tournament Format *</label>
                  <select className="w-full border rounded px-3 py-2 text-sm" value={reg.tournament_format} onChange={setR('tournament_format')}>
                    {T_FORMATS.map((f) => <option key={f}>{f.replace(/_/g,' ')}</option>)}
                  </select>
                </div>
                <Input label="Min Teams" type="number" value={reg.min_teams} onChange={setR('min_teams')} />
                <Input label="Max Teams" type="number" value={reg.max_teams} onChange={setR('max_teams')} placeholder="Leave blank = no limit" />
                {['GROUP_KNOCKOUT'].includes(reg.tournament_format) && (
                  <>
                    <Input label="Teams/Group" type="number" value={reg.teams_per_group} onChange={setR('teams_per_group')} />
                    <Input label="Teams Qualifying/Group" type="number" value={reg.teams_qualifying_per_group} onChange={setR('teams_qualifying_per_group')} />
                  </>
                )}
              </div>
            </Section>

            <Section title="Points System">
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                <Input label="Win" type="number" value={reg.points_for_win} onChange={setR('points_for_win')} />
                <Input label="Loss" type="number" value={reg.points_for_loss} onChange={setR('points_for_loss')} />
                <Input label="Tie" type="number" value={reg.points_for_tie} onChange={setR('points_for_tie')} />
                <Input label="No Result" type="number" value={reg.points_for_no_result} onChange={setR('points_for_no_result')} />
                <Input label="Forfeit Penalty" type="number" value={reg.points_penalty_for_forfeit} onChange={setR('points_penalty_for_forfeit')} />
              </div>
              <div className="mt-3">
                <label className="text-sm font-medium block mb-1">Tiebreaker Order</label>
                <div className="flex flex-wrap gap-2">
                  {TIEBREAKERS.map((tb) => (
                    <label key={tb} className="flex items-center gap-1 text-sm cursor-pointer">
                      <input type="checkbox"
                        checked={reg.tiebreaker_order?.includes(tb)}
                        onChange={(e) => {
                          const arr = reg.tiebreaker_order || [];
                          setReg((p) => ({ ...p, tiebreaker_order: e.target.checked ? [...arr, tb] : arr.filter((x) => x !== tb) }));
                        }}
                      />
                      {tb}
                    </label>
                  ))}
                </div>
              </div>
            </Section>
          </>
        )}
        {isEdit && !canEditReg && (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 text-sm text-yellow-700">
            ⚠️ Regulations cannot be edited once tournament is ONGOING or COMPLETED.
          </div>
        )}

        <div className="flex gap-3">
          <Button type="submit" disabled={loading} className="px-6">
            {loading ? 'Saving...' : isEdit ? 'Update Tournament' : 'Create Tournament'}
          </Button>
          <Button type="button" variant="secondary" onClick={() => navigate('/organizer')}>Cancel</Button>
        </div>
      </form>
    </div>
  );
}

function Section({ title, children }) {
  return (
    <div className="border rounded-xl p-5 bg-white shadow-sm">
      <h3 className="font-semibold text-gray-800 mb-4 pb-2 border-b">{title}</h3>
      {children}
    </div>
  );
}

function CheckRow({ label, checked, onChange }) {
  return (
    <label className="flex items-center gap-2 text-sm cursor-pointer col-span-1">
      <input type="checkbox" checked={checked} onChange={onChange} className="w-4 h-4" />
      {label}
    </label>
  );
}