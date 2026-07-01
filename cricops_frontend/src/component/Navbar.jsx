import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  return (
    <nav className="flex items-center justify-between px-6 py-3 bg-gray-900 text-white">
      <div className="flex gap-4">
        <Link to="/">CricOps</Link>
        <Link to="/matches">Matches</Link>
        <Link to="/venues">Venues</Link>
        <Link to="/players">Players</Link>
        {user?.role === 'TEAMHEAD' && <Link to="/teams">My Team</Link>}
      </div>
      <div className="flex gap-3 items-center">
        {user ? (
          <>
            <span className="text-sm">{user.email} ({user.role})</span>
            <button onClick={() => { logout(); navigate('/login'); }} className="text-sm underline">
              Logout
            </button>
          </>
        ) : (
          <>
            <Link to="/login">Login</Link>
            <Link to="/register">Register</Link>
          </>
        )}
      </div>
    </nav>
  );
}
