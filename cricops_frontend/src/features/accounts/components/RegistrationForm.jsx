import { useState } from 'react';
import Input from '../../../components/Input';
import Button from '../../../components/Button';

const APPLY_OPTIONS = ['ORGANIZER', 'TEAMHEAD', 'UMPIRE'];

export default function RegistrationForm({ onSubmit, loading, error }) {
  const [form, setForm] = useState({email: '', password: '', first_name: '', middle_name: '', last_name: '', phone: '', apply_for: 'TEAMHEAD',});

  const set = (k) => (e) => setForm((prev) => ({ ...prev, [k]: e.target.value }));

  return (
    <form onSubmit={(e) => { e.preventDefault(); onSubmit(form); }}
      className="max-w-sm mx-auto mt-12 p-6 border rounded">
      <h2 className="text-xl font-semibold mb-4">Register</h2>
      <Input label="Email" type="email" value={form.email} onChange={set('email')} required />
      <Input label="Password" type="password" value={form.password} onChange={set('password')} required />
      <Input label="First Name" value={form.first_name} onChange={set('first_name')} required />
      <Input label="Middle Name (optional)" value={form.middle_name} onChange={set('middle_name')} />
      <Input label="Last Name" value={form.last_name} onChange={set('last_name')} required />
      <Input label="Phone" value={form.phone} onChange={set('phone')} required error={Array.isArray(error?.phone) ? error.phone[0] : error?.phone} />
      <div className="mb-3">
        <label className="block text-sm font-medium mb-1">Apply For</label>
        <select className="w-full border rounded px-3 py-2 text-sm"
          value={form.apply_for}
          onChange={set('apply_for')}>
          {APPLY_OPTIONS.map((r) => <option key={r} value={r}>{r}</option>)}
        </select>
      </div>
      {error?.detail && <p className="text-red-500 text-sm mb-2">{error.detail}</p>}
      {typeof error === 'string' && <p className="text-red-500 text-sm mb-2">{error}</p>}
      <Button type="submit" disabled={loading} className="w-full">
        {loading ? 'Registering...' : 'Register'}
      </Button>
    </form>
  );
}