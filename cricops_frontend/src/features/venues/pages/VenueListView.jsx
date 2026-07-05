import { useState } from 'react';
import { useFetch } from '../../../hooks/useFetch';
import { ENDPOINTS } from '../../../api/endpoints';
import VenueCard from '../components/VenueCard';
import VenueFormModal from '../components/VenueFormModal';
import Button from '../../../components/Button';
import { useAuth } from '../../../context/AuthContext';
import { isOrganizer } from '../../../constants/roles';

export default function VenueListView() {
  const { data, loading, refetch } = useFetch(ENDPOINTS.VENUES);
  const { user } = useAuth();
  const [showForm, setShowForm] = useState(false);
  const venues = Array.isArray(data) ? data : data?.results || [];

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold">Venues</h2>
        {isOrganizer(user) && <Button onClick={() => setShowForm(true)}> + Add Venue</Button>}
      </div>
      {loading ? <p>Loading...</p> : (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {venues.map((v) => <VenueCard key={v.venue_id} venue={v} />)}
        </div>
      )}
      {showForm && <VenueFormModal onClose={() => setShowForm(false)} onCreated={refetch} />}
    </div>
  );
}
