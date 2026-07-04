import { useState } from 'react';
import client from '../../../api/client';
import { ENDPOINTS } from '../../../api/endpoints';
import Button from '../../../components/Button';
import { useFetch } from '../../../hooks/useFetch';

export default function TossModal({ match, teamA, teamB, onClose, onDone }) {
  const [winner, setWinner] = useState('');
  const [decision, setDecision] = useState('BAT');
  const [error, setError] = useState(null);

  const submit = async () => {
    try {
      await client.post(ENDPOINTS.SUBMIT_TOSS, {
        match_id: match.match_id, toss_winner_team_id: winner, toss_decision: decision,
      });
      onDone();
      onClose();
    } catch (err) {
      setError(err.response?.data?.error || 'Toss failed');
    }
  };

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center">
      <div className="bg-white p-6 rounded w-80">
        <h3 className="font-semibold mb-3">Submit Toss</h3>
        <select className="w-full border rounded px-3 py-2 text-sm mb-3" value={winner} onChange={(e) => setWinner(e.target.value)}>
          <option value="">Toss winner</option>
          <option value={teamA}>{match.teams?.[0]}</option>
          <option value={teamB}>{match.teams?.[1]}</option>
        </select>
        <select className="w-full border rounded px-3 py-2 text-sm mb-3" value={decision} onChange={(e) => setDecision(e.target.value)}>
          <option value="BAT">Bat</option>
          <option value="BOWL">Bowl</option>
        </select>
        {error && <p className="text-red-500 text-xs mb-2">{error}</p>}
        <div className="flex gap-2">
          <Button onClick={submit}>Submit</Button>
          <Button variant="secondary" onClick={onClose}>Cancel</Button>
        </div>
      </div>
    </div>
  );
}
