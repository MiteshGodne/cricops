import { useState } from 'react';
import client from '../../../api/client';
import { ENDPOINTS } from '../../../api/endpoints';
import Input from '../../../components/Input';
import Button from '../../../components/Button';

const ROLES = ['BATSMAN', 'BOWLER', 'ALL_ROUNDER', 'WICKETKEEPER'];

export default function AddPlayerForm({ teamId, onCreated }) {
  const [form, setForm] = useState({ full_name: '', date_of_birth: '', player_role: 'BATSMAN', nationality: '' });
  const [error, setError] = useState(null);
  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  const submit = async (e) => {
    e.preventDefault();
    try {
      await client.post(ENDPOINTS.PLAYERS, { ...form, current_team: teamId });
      setForm({ full_name: '', date_of_birth: '', player_role: 'BATSMAN', nationality: '' });
      onCreated();
    } catch (err) {
      setError(err.response?.data);
    }
  };

  return (
    <form onSubmit={submit} className="border p-4 rounded mb-4">
      <Input label="Full Name" value={form.full_name} onChange={set('full_name')} required />
      <Input label="DOB" type="date" value={form.date_of_birth} onChange={set('date_of_birth')} required />
      <label className="block text-sm font-medium mb-1">Role</label>
      <select className="w-full border rounded px-3 py-2 text-sm mb-3" value={form.player_role} onChange={set('player_role')}>
        {ROLES.map((r) => <option key={r} value={r}>{r}</option>)}
      </select>
      <Input label="Nationality" value={form.nationality} onChange={set('nationality')} />
      {error && <p className="text-red-500 text-xs mb-2">{JSON.stringify(error)}</p>}
      <Button type="submit">Add Player</Button>
    </form>
  );
}
