"use client";

import { useCallback, useEffect, useState } from "react";

import { ApiError, apiFetch } from "@/lib/api/client";

export function useApiQuery<T>(path: string | null) {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<ApiError | null>(null);
  const [loading, setLoading] = useState(Boolean(path));

  const reload = useCallback(async (overridePath?: string) => {
    const requestPath = overridePath ?? path;
    if (!requestPath) return;
    setLoading(true);
    setError(null);
    try {
      setData(await apiFetch<T>(requestPath));
    } catch (caught) {
      setError(caught instanceof ApiError ? caught : new ApiError("Unexpected error", 0));
    } finally {
      setLoading(false);
    }
  }, [path]);

  useEffect(() => {
    // This hook intentionally synchronizes component state with the API resource.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    void reload();
  }, [reload]);

  return { data, error, loading, reload, setData };
}
