import { useAuth } from '../../../context/AuthContext';

export default function ProfileDashboard() {
  const { user } = useAuth();
  if (!user) return null;

  return (
    <div className="max-w-md mx-auto mt-8 p-6 border rounded">
      <h2 className="text-xl font-semibold mb-4">My Profile</h2>
      <p><strong>Email:</strong> {user.email}</p>
      <p><strong>Name:</strong> {user.first_name} {user.last_name}</p>
      <p><strong>Phone:</strong> {user.phone}</p>
      <p><strong>Role:</strong> {user.role}</p>
      <p><strong>Email Verified:</strong> {user.is_email_verified ? 'Yes' : 'No'}</p>
    </div>
  );
}
