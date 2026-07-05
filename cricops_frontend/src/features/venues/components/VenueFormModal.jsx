import { useState } from 'react';
import client from '../../../api/client';
import { ENDPOINTS } from '../../../api/endpoints';
import Input from '../../../components/Input';
import Button from '../../../components/Button';

export default function VenueFormModal({ onClose, onCreated }) {
  const [form, setForm] = useState({ name: '', address_line: '', city: '', state: '', country: '', pincode: '', capacity: '' });
  const [error, setError] = useState(null);
  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  const submit = async (e) => {
    e.preventDefault();
    try {
      await client.post(ENDPOINTS.VENUES, form);
      onCreated();
      onClose();
    } catch (err) {
      setError(err.response?.data);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center">
      <form onSubmit={submit} className="bg-white p-6 rounded w-96">
        <h3 className="font-semibold mb-3"> + Add Venue</h3>
        <div className='flex'>
          <Input label="Name" value={form.name} onChange={set('name')} required />
          <span className='m-1'></span>
          <Input label="City" value={form.city} onChange={set('city')} required />
        </div>
        <Input label="Address" value={form.address_line} onChange={set('address_line')} required />
        <div className='flex'>
          <Input label="State" value={form.state} onChange={set('state')} />
          <span className='m-1'></span>
          <Input label="Country" value={form.country} onChange={set('country')} />
        </div>
        <div className='flex'>
          <Input label="Pincode" type="number" value={form.pincode} onChange={set('pincode')} />
          <span className='m-1'></span>
          <Input label="Capacity" type="number" value={form.capacity} onChange={set('capacity')} />
        </div>
        {error && <p className="text-red-500 text-xs mb-2">{JSON.stringify(error)}</p>}
        <div className="flex gap-2">
          <Button type="submit">Save</Button>
          <Button type="button" variant="secondary" onClick={onClose}>Cancel</Button>
        </div>
      </form>
    </div>
  );
}
