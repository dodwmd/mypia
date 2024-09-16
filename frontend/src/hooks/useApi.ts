import { useState } from 'react';
// Remove the unused import: import api from '../services/api';

interface ApiResponse<T> {
  data: T;
  status: number;
}

export function useApi<T>() {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<Error | null>(null);
  const [loading, setLoading] = useState<boolean>(false);

  const fetchData = async (url: string): Promise<void> => {
    setLoading(true);
    try {
      const response = await fetch(url);
      const result: ApiResponse<T> = await response.json();
      setData(result.data);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('An unknown error occurred'));
    } finally {
      setLoading(false);
    }
  };

  return { data, error, loading, fetchData };
}
