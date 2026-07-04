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
  const [dismissedId, setDismissedId] = useState('');



    // BallEntryPad.jsx
  const submit = async () => {
    try {
      await client.post(ENDPOINTS.SUBMIT_DELIVERY, {
        innings_id: inningsId, striker_id: strikerId, non_striker_id: nonStrikerId, bowler_id: bowlerId,
        runs_scored: runs, extra_type: extraType, extra_runs: extraRuns,
        wicket_type: wicketType, is_boundary: isBoundary,
        ...(fielderId && { fielder_id: fielderId }),
        ...(dismissedId && { dismissed_player_id: dismissedId }),
      });
      setRuns(0); setExtraType('NONE'); setExtraRuns(0); setWicketType('NONE'); setIsBoundary(false); setFielderId('');
      onDelivered();
    } catch (err) {
      setError(err.response?.data?.error || JSON.stringify(err.response?.data));
    }
  };

  return (
    <div className="rounded-2xl border bg-white shadow-md p-5">
      <h3 className="font-bold text-gray-800 mb-4 text-center tracking-wide">Ball Entry</h3>

      {/* Run circles */}
      <div className="flex flex-wrap justify-center gap-3 mb-4">
        {[0, 1, 2, 3, 4, 5, 6].map((r) => (
          <button key={r} onClick={() => setRuns(r)}
            className={`w-12 h-12 rounded-full font-bold text-sm transition-all duration-200 border-2 ${
              runs === r
                ? 'bg-indigo-600 text-white border-indigo-600 scale-110 shadow-lg'
                : 'bg-white text-gray-700 border-gray-300 hover:border-indigo-400 hover:scale-105'
            }`}>{r}</button>
        ))}
        <input type="number" min={0} placeholder="Custom"
          onChange={(e) => setRuns(Number(e.target.value))}
          className="w-16 h-12 rounded-full text-center border-2 border-gray-300 text-sm focus:border-indigo-500 outline-none" />
      </div>

      {/* Boundary toggle */}
      <div className="flex justify-center mb-5">
        <button onClick={() => setIsBoundary(!isBoundary)}
          className={`px-4 py-1.5 rounded-full text-xs font-semibold border-2 transition-all ${
            isBoundary ? 'bg-amber-400 border-amber-400 text-white shadow-md' : 'bg-white border-gray-300 text-gray-500'
          }`}>
          🏏 Boundary {isBoundary ? 'ON' : 'OFF'}
        </button>
      </div>

      {/* Extras */}
      <div className="mb-4">
        <p className="text-xs font-semibold text-gray-500 mb-2 uppercase tracking-wide">Extra</p>
        <div className="flex flex-wrap gap-2">
          {EXTRAS.map((e) => (
            <button key={e} onClick={() => setExtraType(e)}
              className={`px-3 py-1.5 rounded-full text-xs font-medium border-2 transition-all ${
                extraType === e ? 'bg-sky-500 border-sky-500 text-white' : 'bg-white border-gray-300 text-gray-600 hover:border-sky-400'
              }`}>{e.replace('_', ' ')}</button>
          ))}
          {extraType !== 'NONE' && (
            <input type="number" placeholder="runs" value={extraRuns}
              onChange={(e) => setExtraRuns(Number(e.target.value))}
              className="w-20 rounded-full border-2 border-gray-300 px-3 py-1.5 text-xs text-center focus:border-sky-500 outline-none" />
          )}
        </div>
      </div>

      {/* Wicket */}
      <div className="mb-4">
        <p className="text-xs font-semibold text-gray-500 mb-2 uppercase tracking-wide">Wicket</p>
        <div className="flex flex-wrap gap-2">
          {WICKETS.map((w) => (
            <button key={w} onClick={() => setWicketType(w)}
              className={`px-3 py-1.5 rounded-full text-xs font-medium border-2 transition-all ${
                wicketType === w ? 'bg-red-500 border-red-500 text-white' : 'bg-white border-gray-300 text-gray-600 hover:border-red-400'
              }`}>{w.replace('_', ' ')}</button>
          ))}
        </div>
        {['CAUGHT', 'STUMPED', 'RUN_OUT'].includes(wicketType) && (
          <select value={fielderId} onChange={(e) => setFielderId(e.target.value)}
            className="mt-2 border-2 border-gray-300 rounded-full px-3 py-1.5 text-xs focus:border-red-400 outline-none">
            <option value="">Fielder</option>
            {fielders.map((f) => <option key={f.player_id} value={f.player_id}>{f.full_name}</option>)}
          </select>
        )}
        {wicketType !== 'NONE' && (
          <select value={dismissedId} onChange={(e) => setDismissedId(e.target.value)}
            className="mt-2 ml-2 border-2 rounded-full px-3 py-1.5 text-xs">
            <option value="">Who's out? (default: striker)</option>
            <option value={strikerId}>Striker</option>
            <option value={nonStrikerId}>Non-striker</option>
          </select>
        )}
      </div>

      {error && <p className="text-red-500 text-xs mb-3 text-center">{error}</p>}
      <button onClick={submit}
        className="w-full py-2.5 rounded-full bg-gradient-to-r from-indigo-600 to-blue-500 text-white font-bold shadow-md hover:shadow-lg hover:scale-[1.01] transition-all">
        Submit Ball
      </button>
    </div>
  );
}
