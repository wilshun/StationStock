"use client";
import { ShieldAlert } from "lucide-react";
import Link from "next/link";
import type { ReactNode } from "react";
import { useAuth } from "@/components/auth/auth-provider";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
export function ManagerRoute({ children }: { children: ReactNode }) {
  const { user } = useAuth();
  if (user?.role === "manager") return children;
  return <Card className="mx-auto max-w-lg border-amber-200"><CardHeader><CardTitle className="flex items-center gap-2"><ShieldAlert /> Manager access required</CardTitle></CardHeader><CardContent><p className="mb-4 text-slate-600">Your employee account can view inventory, but cannot change administrative records.</p><Button render={<Link href="/dashboard" />}>Return to dashboard</Button></CardContent></Card>;
}
