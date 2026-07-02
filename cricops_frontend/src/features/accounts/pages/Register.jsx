import { useNavigate, Link } from 'react-router-dom';
import RegistrationForm from '../components/RegistrationForm';
import { useAuthActions } from '../hooks/useAuthActions';

export default function Register() {
  const { doRegister, loading, error } = useAuthActions();
  const navigate = useNavigate();

  const handleSubmit = async (payload) => {
    const ok = await doRegister(payload);
    if (ok) navigate('/login');
  };

  return (
    <div>
      <RegistrationForm onSubmit={handleSubmit} loading={loading} error={error} />
      <p className="text-center text-sm mt-2">
        Already have an account? <Link to="/login" className="text-blue-600 underline">Login</Link>
      </p>
    </div>
  );
}