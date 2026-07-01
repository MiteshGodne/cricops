import { useState } from 'react';
import { useAuth } from '../../../context/AuthContext';

export function useAuthActions() {
  const { login, register } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const doLogin = async (email, password) => {
    setLoading(true);
    setError(null);
    try {
      await login(email, password);
      return true;
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed');
      return false;
    } finally {
      setLoading(false);
    }
  };

  const doRegister = async (payload) => {
    setLoading(true);
    setError(null);
    try {
      await register(payload);
      return true;
    } catch (err) {
      setError(err.response?.data || { detail: 'Registration failed' });
      return false;
    } finally {
      setLoading(false);
    }
  };

  return { doLogin, doRegister, loading, error };
}
