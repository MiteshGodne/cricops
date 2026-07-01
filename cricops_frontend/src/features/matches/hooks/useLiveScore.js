import { useState, useEffect, useCallback } from 'react';
import client from '../../../api/client';
import { ENDPOINTS } from '../../../api/endpoints';

export function useLiveScore(matchId, intervalMs = 5000) {
  const [score, setScore] = useState(null);
  const [error, setError] = useState(null);

  const fetchScore = useCallback(async () => {
    try {
      const { data } = await client.get(ENDPOINTS.LIVE_SCORE(matchId));
      setScore(data);
      setError(null);
    } catch (err) {
      setError(err.response?.data?.error || 'No live score');
    }
  }, [matchId]);

  useEffect(() => {
    fetchScore();
    const id = setInterval(fetchScore, intervalMs);
    return () => clearInterval(id);
  }, [fetchScore, intervalMs]);

  return { score, error, refetch: fetchScore };
}
