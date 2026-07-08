export default function VenueCard({ venue }) {
  return (
    <div className="border-l-5 border-b-5 border-blue-300 rounded-xl bg-blue-50 p-4">
      <h3 className="font-semibold text-l">{venue.name}</h3>
      <p className="text-m text-gray-800">{venue.address_line}</p>
      <p className="text-sm text-gray-600">{venue.city}, {venue.state}</p>
      <p className="text-sm text-gray-600">Capacity: {venue.capacity ?? 'N/A'}</p>
    </div>
  );
}
