import { useState } from 'react';
import { useAuth } from '../../../context/AuthContext';
import client from '../../../api/client';
import { ENDPOINTS } from '../../../api/endpoints';
import Input from '../../../components/Input';
import Button from '../../../components/Button';
import BackButton from '../../../components/BackButton';

export default function ProfileDashboard() {
  const { user, refreshUser } = useAuth();
  const [editing, setEditing] = useState(false);
  const [form, setForm] = useState({
    first_name: user?.first_name || '',
    middle_name: user?.middle_name || '',
    last_name: user?.last_name || '',
    phone: user?.phone || '',
  });
  const [avatar, setAvatar] = useState(null);
  const [preview, setPreview] = useState(null);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  const set = (k) => (e) => setForm((p) => ({ ...p, [k]: e.target.value }));

  const handleAvatarChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setAvatar(file);
    setPreview(URL.createObjectURL(file));
  };

  const save = async (e) => {
    e.preventDefault();
    setError(null);
    try {
      const fd = new FormData();
      Object.entries(form).forEach(([k, v]) => fd.append(k, v));
      if (avatar) fd.append('avatar_url', avatar);
      await client.patch(`${ENDPOINTS.USERS}${user.user_id}/`, fd, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      await refreshUser();
      setEditing(false);
      setSuccess(true);
      setTimeout(() => setSuccess(false), 2000);
    } catch (err) {
      setError(err.response?.data);
    }
  };

  if (!user) return null;

  const avatarSrc = preview || (user.avatar_url ? `http://127.0.0.1:8000${user.avatar_url}` : null);

  return (
    <div className="max-w-md mx-auto mt-8 p-6 border rounded">
      <h2 className="text-xl font-semibold mb-4">My Profile</h2>

      {/* Avatar */}
      <div className="flex items-center gap-4 mb-6">
        <div className="w-16 h-16 rounded-full bg-[#efa800] flex items-center justify-center text-white text-2xl font-bold overflow-hidden">
          {avatarSrc ? <img src={avatarSrc} alt="avatar" className="w-full h-full object-cover" /> : (user.first_name?.[0] || '?')}
        </div>
        {editing && (
          <label className="text-sm text-blue-600 underline cursor-pointer">
            Change photo
            <input type="file" accept="image/*" className="hidden" onChange={handleAvatarChange} />
          </label>
        )}
      </div>

      {!editing ? (
        <>
          <p><strong>Name:</strong> {user.first_name} {user.middle_name} {user.last_name}</p>
          <p className="mt-1"><strong>Email:</strong> {user.email}</p>
          <p className="mt-1"><strong>Phone:</strong> {user.phone}</p>
          {user.is_superuser ? <p className="mt-1"><strong>Role:</strong> SUPERUSER </p> :
            <>
              <p className="mt-1"><strong>Role:</strong> {user.role}</p>
              <p className="mt-1"><strong>Applied for:</strong> {user.apply_for}</p>
            </>}
          <p className="mt-1"><strong>Email Verified:</strong> {user.is_email_verified ? 'Yes' : 'No'}</p>
          {success && <p className="text-green-600 text-sm mt-2">Saved!</p>}
          <Button className="mt-4" onClick={() => setEditing(true)}>Edit Profile</Button>
        </>
      ) : (
        <form onSubmit={save}>
          <Input label="First Name" value={form.first_name} onChange={set('first_name')} required />
          <Input label="Middle Name" value={form.middle_name} onChange={set('middle_name')} />
          <Input label="Last Name" value={form.last_name} onChange={set('last_name')} required />
          <Input label="Phone" value={form.phone} onChange={set('phone')} required />
          {error && <p className="text-red-500 text-xs mb-2">{JSON.stringify(error)}</p>}
          <div className="flex gap-2 mt-2 items-center">
            <Button type="submit">Save</Button>
            <BackButton type="button" onClick={() => { setEditing(false); setPreview(null); setAvatar(null); }}>Cancel</BackButton>
          </div>
        </form>
      )}
    </div>
  );
}