import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Skeleton from '../components/Skeleton';

export default function ProtectedRoute({ children, allowedRoles }) {
  const { user, loading } = useAuth();
  
  if (loading) return <Skeleton rows={4} />;
  // if (loading) return <div className="p-8 text-center">Loading...</div>;

  if (!user) return <Navigate to="/login" replace />;
  if (allowedRoles && !allowedRoles.includes(user.role)) {
    return <Navigate to="/" replace />;
  }
  return children;
}