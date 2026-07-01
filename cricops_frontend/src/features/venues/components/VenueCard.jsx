export default function VenueCard({ venue }) {
  return (
    <div className="border rounded p-4">
      <h3 className="font-semibold">{venue.name}</h3>
      <p className="text-sm text-gray-600">{venue.city}, {venue.state}</p>
      <p className="text-xs text-gray-500">Capacity: {venue.capacity ?? 'N/A'}</p>
    </div>
  );
}
