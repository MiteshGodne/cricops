import { useState } from 'react';
import client from '../../../api/client';
import { ENDPOINTS } from '../../../api/endpoints';
import Button from '../../../components/Button';

const EXTRAS = ['NONE', 'WIDE', 'NO_BALL', 'BYE', 'LEG_BYE'];
const WICKETS = ['NONE', 'BOWLED', 'CAUGHT', 'LBW', 'RUN_OUT', 'STUMPED', 'HIT_WICKET'];

export default function BallEntryPad({ inningsId, strikerId, nonStrikerId, bowlerId, fielders, onDelivered }) {
  const [runs, setRuns] = useState(0);
  const [extraType, setExtraType] = useState('NONE');
  const [extraRuns, setExtraRuns] = useState(0);
  const [wicketType, setWicketType] = useState('NONE');
  const [fielderId, setFielderId] = useState('');
  const [isBoundary, setIsBoundary] = useState(false);
  const [error, setError] = useState(null);

  const submit = async () => {
    try {
      await client.post(ENDPOINTS.SUBMIT_DELIVERY, {
        innings_id: inningsId, striker_id: strikerId, non_striker_id: nonStrikerId, bowler_id: bowlerId,
        runs_scored: runs, extra_type: extraType, extra_runs: extraRuns,
        wicket_type: wicketType, is_boundary: isBoundary,
        ...(fielderId && { fielder_id: fielderId }),
      });
      setRuns(0); setExtraType('NONE'); setExtraRuns(0); setWicketType('NONE'); setIsBoundary(false); setFielderId('');
      onDelivered();
    } catch (err) {
      setError(err.response?.data?.error || JSON.stringify(err.response?.data));
    }
  };

  return (
    <div className="border rounded p-4">
      <h3 className="font-semibold mb-2">Ball Entry</h3>
      <div className="grid grid-cols-4 gap-2 mb-3">
        {[0, 1, 2, 3, 4, 5, 6].map((r) => (
          <button key={r} onClick={() => { setRuns(r); setIsBoundary(r === 4 || r === 6); }}
            className={`border rounded py-2 ${runs === r ? 'bg-blue-600 text-white' : ''}`}>{r}</button>
        ))}
      </div>
      <div className="flex gap-2 mb-3">
        <select className="border rounded px-2 py-1 text-sm" value={extraType} onChange={(e) => setExtraType(e.target.value)}>
          {EXTRAS.map((e) => <option key={e} value={e}>{e}</option>)}
        </select>
        {extraType !== 'NONE' && (
          <input className="border rounded px-2 py-1 text-sm w-20" type="number" placeholder="Extra runs" value={extraRuns} onChange={(e) => setExtraRuns(Number(e.target.value))} />
        )}
      </div>
      <div className="flex gap-2 mb-3">
        <select className="border rounded px-2 py-1 text-sm" value={wicketType} onChange={(e) => setWicketType(e.target.value)}>
          {WICKETS.map((w) => <option key={w} value={w}>{w}</option>)}
        </select>
        {['CAUGHT', 'STUMPED', 'RUN_OUT'].includes(wicketType) && (
          <select className="border rounded px-2 py-1 text-sm" value={fielderId} onChange={(e) => setFielderId(e.target.value)}>
            <option value="">Fielder</option>
            {fielders.map((f) => <option key={f.player_id} value={f.player_id}>{f.full_name}</option>)}
          </select>
        )}
      </div>
      {error && <p className="text-red-500 text-xs mb-2">{error}</p>}
      <Button onClick={submit}>Submit Ball</Button>
    </div>
  );
}
