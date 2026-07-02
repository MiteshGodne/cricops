import { useState, useEffect, useCallback } from 'react';
import client from '../api/client';

export function useFetch(url, deps = []) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const refetch = useCallback(async () => {
    setLoading(true);
    try {
      const res = await client.get(url);
      setData(res.data);
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  }, [url]);

  useEffect(() => { if (url) refetch(); }, [url]);

  return { data, loading, error, refetch };
}
