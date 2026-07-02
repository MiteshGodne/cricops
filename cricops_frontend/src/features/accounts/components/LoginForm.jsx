import { useState } from 'react';
import Input from '../../../components/Input';
import Button from '../../../components/Button';

export default function LoginForm({ onSubmit, loading, error }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  return (
    <form
      onSubmit={(e) => { e.preventDefault(); onSubmit(email, password); }}
      className="max-w-sm mx-auto mt-12 p-6 border rounded"
    >
      <h2 className="text-xl font-semibold mb-4">Login</h2>
      <Input label="Email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
      <Input label="Password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
      {error && <p className="text-red-500 text-sm mb-2">{error}</p>}
      <Button type="submit" disabled={loading} className="w-full">
        {loading ? 'Loading...' : 'Login'}
      </Button>
    </form>
  );
}
