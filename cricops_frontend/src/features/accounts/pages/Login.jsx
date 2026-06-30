import { useNavigate } from 'react-router-dom';
import LoginForm from '../components/LoginForm';
import { useAuthActions } from '../hooks/useAuthActions';

export default function Login() {
  const { doLogin, loading, error } = useAuthActions();
  const navigate = useNavigate();

  const handleSubmit = async (email, password) => {
    const ok = await doLogin(email, password);
    if (ok) navigate('/');
  };

  return <LoginForm onSubmit={handleSubmit} loading={loading} error={error} />;
}
