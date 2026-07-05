import { useParams, Link } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { useFetch } from '../../../hooks/useFetch';
import { ENDPOINTS } from '../../../api/endpoints';
import client from '../../../api/client';
import Button from '../../../components/Button';
import BackButton from '../../../components/BackButton';
import TossModal from '../../matches/components/TossModal';
import toast from 'react-hot-toast';

const ROUND_TYPES = ['LEAGUE', 'QUALIFIER', 'QUARTERFINAL', 'SEMIFINAL', 'FINAL'];

export default function MatchManage() {
  const { matchId } = useParams();
  const { data: match, refetch } = useFetch(`${ENDPOINTS.MATCHES}${matchId}/`);
  const { data: tmData, refetch: refetchTM } = useFetch(`${ENDPOINTS.TEAM_MATCHES}?match=${matchId}`);
  const { data: venuesData } = useFetch(ENDPOINTS.VENUES);
  const { data: acceptedApps } = useFetch(match ? `${ENDPOINTS.APPLICATIONS}?tournament=${match.tournament}&status=ACCEPTED` : null);

  const teamMatches = Array.isArray(tmData) ? tmData : tmData?.results || [];
  const accepted = Array.isArray(acceptedApps) ? acceptedApps : acceptedApps?.results || [];
  const venues = Array.isArray(venuesData) ? venuesData : venuesData?.results || [];
  const [showToss, setShowToss] = useState(false);
  const [addTeam, setAddTeam] = useState('');
  const [addSide, setAddSide] = useState('A');

  const [isEditing, setIsEditing] = useState(false);
  const [editForm, setEditForm] = useState({
    round_type: '',
    round_number: 1,
    start_date: '',
    venue: ''
  });

  useEffect(() => {
    if (match) {
      setEditForm({
        round_type: match.round_type || 'LEAGUE',
        round_number: match.round_number || 1,
        start_date: match.start_date ? match.start_date.substring(0, 16) : '',
        venue: match.venue || '',
      });
    }
  }, [match]);

  const handleUpdateMatch = async (e) => {
    e.preventDefault();
    try {
      await client.patch(`${ENDPOINTS.MATCHES}${matchId}/`, {
        round_type: editForm.round_type,
        round_number: Number(editForm.round_number),
        start_date: editForm.start_date || null,
        venue: editForm.venue || null,
        tournament: match.tournament
      });
      toast.success('Match details updated');
      setIsEditing(false);
      refetch();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to update match data.');
    }
  };

  const addTeamToMatch = async () => {
    try {
      await client.post(ENDPOINTS.TEAM_MATCHES, { match: matchId, team: addTeam, side: addSide });
      toast.success('Team added');
      refetchTM();
    } catch (err) { toast.error(err.response?.data?.error || 'Failed'); }
  };

  const abandon = async () => {
    const reason = prompt('Reason for abandoning?');
    try {
      await client.post(ENDPOINTS.ABANDON_MATCH(matchId), { reason });
      toast.success('Match abandoned');
      refetch();
    } catch { toast.error('Failed'); }
  };

  const teamA = teamMatches.find((t) => t.side === 'A');
  const teamB = teamMatches.find((t) => t.side === 'B');

  if (!match) return <p>Loading...</p>;

  return (
    <div className="max-w-2xl mx-auto">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold">Match Management</h2>
        <Link to={`/organizer/tournaments/${match.tournament}/manage`} className="text-sm text-blue-600 underline">
          <BackButton>Back</BackButton>
        </Link>
      </div>
      <div className="border rounded p-4 mb-4 bg-white relative">
        <div className="flex justify-between items-center mb-3">
          <h3 className="font-semibold text-gray-700">Match Overview</h3>
          <Button
            className="text-xs py-1 px-3"
            onClick={() => setIsEditing(!isEditing)}
          >
            {isEditing ? 'Cancel' : 'Edit Details'}
          </Button>
        </div>

        {isEditing ? (
          <form onSubmit={handleUpdateMatch} className="space-y-3">
            <div className='grid grid-cols-2 items-center'>
              <div className='mr-2'>
                <label className="block text-xs font-medium text-gray-600 mb-1">Round Type</label>
                <select className="border rounded w-full px-3 py-1.5 text-sm" value={editForm.round_type}
                  onChange={(e) => setEditForm({ ...editForm, round_type: e.target.value })}
                >
                  {ROUND_TYPES.map((r) => <option key={r}>{r}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1">Venue</label>
                <select className="border rounded w-full px-3 py-1.5 text-sm" value={editForm.venue} onChange={(e) => setEditForm({ ...editForm, venue: e.target.value })} required>
                  <option value="">Select venue</option>
                  {venues.map((v) => <option key={v.venue_id} value={v.venue_id}>{v.name}, {v.city}</option>)}
                </select>
              </div>
            </div>

            <div className='grid grid-cols-2 items-center'>
              <div className='mr-2'>
                <label className="block text-xs font-medium text-gray-600 mb-1">Start Date & Time</label>
                <input
                  type="datetime-local"
                  className="border rounded w-full px-3 py-1.5 text-sm"
                  value={editForm.start_date}
                  onChange={(e) => setEditForm({ ...editForm, start_date: e.target.value })}
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-600 mb-1">Round Number</label>
                <input
                  type="number"
                  className="border rounded w-full px-3 py.1.5 py-1"
                  value={editForm.round_number}
                  onChange={(e) => setEditForm({ ...editForm, round_number: e.target.value })}
                />
              </div>
            </div>

            <Button type="submit" className="w-full text-sm mt-2">Save Changes</Button>
          </form>
        ) : (
          <div className="space-y-1">
            <p><strong>Round:</strong> {match.round_type} R{match.round_number}</p>
            <p><strong>Status:</strong> {match.status}</p>
            <p><strong>Start:</strong> {match.start_date ? new Date(match.start_date).toLocaleString() : 'TBD'}</p>
          </div>
        )}
      </div>

      {/* Add teams */}
      <div className="border rounded p-4 mb-4">
        <h3 className="font-semibold mb-3">Teams in Match</h3>
        {teamMatches.map((tm) => (
          <p key={tm.id} className="text-sm mb-1">Side {tm.side}: {tm.team_name || tm.team} {tm.is_toss_winner ? '(Toss Winner)' : ''}</p>
        ))}
        {teamMatches.length < 2 && (
          <div className="flex gap-2 mt-3">
            <select className="border rounded px-3 py-2 text-sm"
              value={addTeam} onChange={(e) => setAddTeam(e.target.value)}>
              <option value="">Select team</option>
              {accepted.map((a) => (
                <option key={a.application_id} value={a.team}>{a.registered_name}</option>
              ))}
            </select>
            <select className="border rounded px-3 py-2 text-sm" value={addSide} onChange={(e) => setAddSide(e.target.value)}>
              <option value="A">Side A</option>
              <option value="B">Side B</option>
            </select>
            <Button onClick={addTeamToMatch}> + Add</Button>
          </div>
        )}
      </div>

      {/* Abandon */}
      {['SCHEDULED', 'LIVE'].includes(match.status) && (
        <Button variant="danger" onClick={abandon}>Abandon Match</Button>
      )}
    </div>
  );
}