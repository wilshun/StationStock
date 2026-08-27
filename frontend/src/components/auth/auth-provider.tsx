"use client";

import { useRouter } from "next/navigation";
import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";

import { ApiError, apiFetch } from "@/lib/api/client";
import type { CurrentUser } from "@/lib/api/types";

interface AuthContextValue {
  user: CurrentUser | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<CurrentUser>;
  logout: () => Promise<void>;
  refresh: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [user, setUser] = useState<CurrentUser | null>(null);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    try {
      setUser(await apiFetch<CurrentUser>("/auth/me"));
    } catch (error) {
      if (!(error instanceof ApiError) || error.status !== 401) throw error;
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    // Loading the server-owned session is the purpose of this mount effect.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    void refresh();
    const handleUnauthorized = () => {
      setUser(null);
      setLoading(false);
      router.replace("/login");
    };
    window.addEventListener("stationstock:unauthorized", handleUnauthorized);
    return () => window.removeEventListener("stationstock:unauthorized", handleUnauthorized);
  }, [refresh, router]);

  const login = useCallback(async (email: string, password: string) => {
    const authenticated = await apiFetch<CurrentUser>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
    setUser(authenticated);
    return authenticated;
  }, []);

  const logout = useCallback(async () => {
    try {
      await apiFetch<{ status: string }>("/auth/logout", { method: "POST" });
    } finally {
      setUser(null);
      router.replace("/login");
    }
  }, [router]);

  const value = useMemo(
    () => ({ user, loading, login, logout, refresh }),
    [user, loading, login, logout, refresh],
  );
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used within AuthProvider");
  return context;
}
