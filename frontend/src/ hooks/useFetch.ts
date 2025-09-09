import { useState, useEffect } from "react";

export const useFetch = <T>(url: string) => {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<any>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);

    // placeholder, no real fetch yet
    setTimeout(() => {
      setData(null);
      setLoading(false);
    }, 500);
  }, [url]);

  return { data, loading, error };
};
