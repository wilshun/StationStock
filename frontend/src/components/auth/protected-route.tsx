"use client";

import { usePathname, useRouter } from "next/navigation";
import { useEffect } from "react";

import { Skeleton } from "@/components/ui/skeleton";
import { useAuth } from "./auth-provider";

export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    if (!loading && !user) router.replace(`/login?next=${encodeURIComponent(pathname)}`);
  }, [loading, pathname, router, user]);

  if (loading || !user) {
    return (
      <div className="mx-auto flex min-h-screen max-w-6xl flex-col gap-5 p-8" aria-label="Loading account">
        <Skeleton className="h-12 w-56" />
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }
  return children;
}
