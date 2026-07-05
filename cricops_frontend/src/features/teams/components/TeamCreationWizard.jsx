import { useState } from 'react';
import client from '../../../api/client';
import { ENDPOINTS } from '../../../api/endpoints';
import Input from '../../../components/Input';
import Button from '../../../components/Button';

export default function TeamCreationWizard({ onCreated }) {
  const [form, setForm] = useState({ team_name: '', short_name: '', city: '', state: '' });
  const [error, setError] = useState(null);
  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  const submit = async (e) => {
    e.preventDefault();
    try {
      const { data } = await client.post(ENDPOINTS.TEAMS, form);
      onCreated(data);
    } catch (err) {
      setError(err.response?.data);
    }
  };

  return (
    <form onSubmit={submit} className="border-2 border-[#183153] p-4 rounded mb-4 max-w-sm">
      <h3 className="font-semibold mb-2">Create Team</h3>
      <Input label="Team Name" value={form.team_name} onChange={set('team_name')} required />
      <Input label="Short Name" value={form.short_name} onChange={set('short_name')} required maxLength={10} />
      <Input label="City" value={form.city} onChange={set('city')} required />
      <Input label="State" value={form.state} onChange={set('state')} required />
      {error && <p className="text-red-500 text-xs mb-2">{JSON.stringify(error)}</p>}
      <Button type="submit">Create</Button>
    </form>
  );
}
