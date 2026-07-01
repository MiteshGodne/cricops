import { useNavigate } from 'react-router-dom';
import RegistrationForm from '../components/RegistrationForm';
import { useAuthActions } from '../hooks/useAuthActions';

export default function Register() {
  const { doRegister, loading, error } = useAuthActions();
  const navigate = useNavigate();

  const handleSubmit = async (payload) => {
    const ok = await doRegister(payload);
    if (ok) navigate('/login');
  };

  return <RegistrationForm onSubmit={handleSubmit} loading={loading} error={error} />;
}
