const COLORS = {
  PENDING: 'bg-yellow-100 text-yellow-800',
  ACCEPTED: 'bg-green-100 text-green-800',
  REJECTED: 'bg-red-100 text-red-800',
  WITHDRAWN: 'bg-gray-100 text-gray-800',
};

export default function ApplicationStatusBadge({ status }) {
  return <span className={`px-2 py-1 rounded text-xs ${COLORS[status] || ''}`}>{status}</span>;
}
