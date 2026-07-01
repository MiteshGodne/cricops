import { useState } from 'react';
import Input from '../../../components/Input';
import Button from '../../../components/Button';

const ROLE_OPTIONS = ['ORGANIZER', 'TEAMHEAD', 'UMPIRE'];

export default function RegistrationForm({ onSubmit, loading, error }) {
  const [form, setForm] = useState({
    email: '', password: '', first_name: '', middle_name: '', last_name: '', phone: '', role: 'TEAMHEAD',
  });

  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  return (
    <form
      onSubmit={(e) => { e.preventDefault(); onSubmit(form); }}
      className="max-w-sm mx-auto mt-12 p-6 border rounded"
    >
      <h2 className="text-xl font-semibold mb-4">Register</h2>
      <Input label="Email" type="email" value={form.email} onChange={set('email')} required />
      <Input label="Password" type="password" value={form.password} onChange={set('password')} required />
      <Input label="First Name" value={form.first_name} onChange={set('first_name')} required />
      <Input label="Last Name" value={form.last_name} onChange={set('last_name')} required />
      <Input label="Phone" value={form.phone} onChange={set('phone')} required error={error?.phone?.[0]} />
      <label className="block text-sm font-medium mb-1">Apply For</label>
      <select className="w-full border rounded px-3 py-2 text-sm mb-3" value={form.role} onChange={set('role')}>
        {ROLE_OPTIONS.map((r) => <option key={r} value={r}>{r}</option>)}
      </select>
      {error && <p className="text-red-500 text-sm mb-2">{error.detail || 'Check fields'}</p>}
      <Button type="submit" disabled={loading} className="w-full">
        {loading ? 'Registering...' : 'Register'}
      </Button>
    </form>
  );
}
