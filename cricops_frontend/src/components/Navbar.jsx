import { useState, useRef, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const NAV_LINKS = [
  { to: '/tournaments', label: 'Tournaments' },
  { to: '/matches', label: 'Matches' },
  { to: '/venues', label: 'Venues' },
  { to: '/players', label: 'Players' },
];

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [menuOpen, setMenuOpen] = useState(false);
  const [profileOpen, setProfileOpen] = useState(false);
  const profileRef = useRef(null);

  // close profile dropdown on outside click
  useEffect(() => {
    const handler = (e) => {
      if (profileRef.current && !profileRef.current.contains(e.target)) {
        setProfileOpen(false);
      }
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  const links = [
    ...(user?.role === 'ORGANIZER' ? [{ to: '/organizer', label: 'Dashboard' }] : []),
    ...(user?.role === 'TEAMHEAD' ? [{ to: '/teamhead', label: 'Dashboard' }] : []),
    ...(user?.role === 'UMPIRE' ? [{ to: '/umpire', label: 'Dashboard' }] : []),
    ...NAV_LINKS,
  ];

  return (
    <nav className="bg-gray-900 text-white px-4 py-3">
      <div className="max-w-6xl mx-auto flex items-center justify-between">
        {/* Logo */}
        <Link to="/" className="font-bold text-lg shrink-0">CricOps</Link>

        {/* Desktop nav links — centered */}
        <div className="hidden md:flex gap-6 absolute left-1/2 -translate-x-1/2">
          {links.map((l) => (
            <Link key={l.to} to={l.to} className="text-sm hover:text-blue-400 transition">
              {l.label}
            </Link>
          ))}
        </div>

        {/* Right side */}
        <div className="flex items-center gap-3">
          {user ? (
            <div className="relative" ref={profileRef}>
              <button
                onClick={() => setProfileOpen((o) => !o)}
                className="w-9 h-9 rounded-full bg-blue-600 flex items-center justify-center text-sm font-bold uppercase"
              >
                {user.first_name?.[0] || user.email?.[0]}
              </button>
              {profileOpen && (
                <div className="absolute right-0 mt-2 w-52 bg-white text-gray-800 rounded shadow-lg z-50">
                  <div className="px-4 py-3 border-b">
                    <p className="font-semibold text-sm">{user.first_name} {user.last_name}</p>
                    <p className="text-xs text-gray-500 truncate">{user.email}</p>
                    <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded mt-1 inline-block">
                      {user.role}
                    </span>
                  </div>
                  <Link to="/profile"
                    onClick={() => setProfileOpen(false)}
                    className="block px-4 py-2 text-sm hover:bg-gray-100">
                    View Profile
                  </Link>
                  <button
                    onClick={() => { logout(); navigate('/login'); setProfileOpen(false); }}
                    className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-gray-100">
                    Logout
                  </button>
                </div>
              )}
            </div>
          ) : (
            <div className="hidden md:flex gap-3 text-sm">
              <Link to="/login" className="hover:text-blue-400">Login</Link>
              <Link to="/register" className="bg-blue-600 px-3 py-1 rounded hover:bg-blue-700">Register</Link>
            </div>
          )}

          {/* Hamburger */}
          <button className="md:hidden" onClick={() => setMenuOpen((o) => !o)}>
            <span className="text-2xl">{menuOpen ? '✕' : '☰'}</span>
          </button>
        </div>
      </div>

      {/* Mobile menu */}
      {menuOpen && (
        <div className="md:hidden mt-3 flex flex-col gap-2 pb-3 border-t border-gray-700 pt-3">
          {links.map((l) => (
            <Link key={l.to} to={l.to}
              onClick={() => setMenuOpen(false)}
              className="text-sm px-2 py-1 hover:text-blue-400">
              {l.label}
            </Link>
          ))}
          {!user && (
            <>
              <Link to="/login" onClick={() => setMenuOpen(false)} className="text-sm px-2 py-1">Login</Link>
              <Link to="/register" onClick={() => setMenuOpen(false)} className="text-sm px-2 py-1">Register</Link>
            </>
          )}
        </div>
      )}
    </nav>
  );
}