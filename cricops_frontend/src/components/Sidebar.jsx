import { Link } from 'react-router-dom';

export default function Sidebar({ links = [] }) {
  return (
    <aside className="w-56 bg-gray-100 p-4 min-h-screen">
      {links.map((l) => (
        <Link key={l.to} to={l.to} className="block py-2 text-sm hover:text-blue-600">
          {l.label}
        </Link>
      ))}
    </aside>
  );
}
