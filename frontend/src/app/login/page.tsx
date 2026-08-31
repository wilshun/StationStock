"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { Boxes } from "lucide-react";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { useAuth } from "@/components/auth/auth-provider";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ApiError } from "@/lib/api/client";

const loginSchema = z.object({
  email: z.string().trim().min(3, "Enter your email address").includes("@", { message: "Enter a valid email address" }),
  password: z.string().min(1, "Enter your password"),
});
type LoginValues = z.infer<typeof loginSchema>;

function LoginForm() {
  const developmentDemoEmail = process.env.NEXT_PUBLIC_DEMO_EMAIL;
  const developmentDemoPassword = process.env.NEXT_PUBLIC_DEMO_PASSWORD;
  const showDevelopmentDemo = process.env.NODE_ENV === "development" && Boolean(developmentDemoEmail && developmentDemoPassword);
  const { login, user, loading } = useAuth();
  const router = useRouter();
  const params = useSearchParams();
  const [serverError, setServerError] = useState<string | null>(null);
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<LoginValues>({ resolver: zodResolver(loginSchema) });

  useEffect(() => {
    if (!loading && user) router.replace("/dashboard");
  }, [loading, router, user]);

  async function onSubmit(values: LoginValues) {
    setServerError(null);
    try {
      await login(values.email, values.password);
      const next = params.get("next");
      router.replace(next?.startsWith("/") ? next : "/dashboard");
    } catch (error) {
      setServerError(error instanceof ApiError ? error.message : "Unable to sign in.");
    }
  }

  return (
    <main className="grid min-h-screen bg-slate-950 lg:grid-cols-2">
      <section className="hidden p-12 text-white lg:flex lg:flex-col lg:justify-between">
        <div className="flex items-center gap-3"><span className="grid size-11 place-items-center rounded-xl bg-emerald-500 text-slate-950"><Boxes /></span><span className="text-xl font-semibold">StationStock</span></div>
        <div className="max-w-xl"><p className="text-sm font-semibold uppercase tracking-[0.22em] text-emerald-400">Know what is on the shelf</p><h1 className="mt-5 text-5xl font-semibold leading-tight tracking-tight">Count faster. Restock with confidence.</h1><p className="mt-5 text-lg leading-8 text-slate-300">A focused inventory workspace for convenience-store teams.</p></div>
        <p className="text-sm text-slate-400">Core MVP{showDevelopmentDemo ? " · Local development environment" : ""}</p>
      </section>
      <section className="flex items-center justify-center bg-slate-50 p-5 sm:p-10">
        <Card className="w-full max-w-md border-slate-200 shadow-xl shadow-slate-950/5">
          <CardHeader><CardTitle className="text-2xl">Welcome back</CardTitle><CardDescription>Sign in to manage inventory and counts.</CardDescription></CardHeader>
          <CardContent>
            {serverError && <Alert variant="destructive" className="mb-5"><AlertTitle>Sign-in failed</AlertTitle><AlertDescription>{serverError}</AlertDescription></Alert>}
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-5" noValidate>
              <div className="space-y-2"><Label htmlFor="email">Email</Label><Input id="email" type="email" autoComplete="email" aria-invalid={Boolean(errors.email)} aria-describedby={errors.email ? "email-error" : undefined} {...register("email")} />{errors.email && <p id="email-error" className="text-sm text-red-600">{errors.email.message}</p>}</div>
              <div className="space-y-2"><Label htmlFor="password">Password</Label><Input id="password" type="password" autoComplete="current-password" aria-invalid={Boolean(errors.password)} aria-describedby={errors.password ? "password-error" : undefined} {...register("password")} />{errors.password && <p id="password-error" className="text-sm text-red-600">{errors.password.message}</p>}</div>
              <Button type="submit" className="min-h-11 w-full bg-emerald-700 hover:bg-emerald-800" disabled={isSubmitting}>{isSubmitting ? "Signing in…" : "Sign in"}</Button>
            </form>
            {showDevelopmentDemo && <div className="mt-6 rounded-lg border border-amber-200 bg-amber-50 p-4 text-sm text-amber-950"><p className="font-medium">Development demo only</p><p className="mt-1">Manager: {developmentDemoEmail}</p><p>Password: {developmentDemoPassword}</p></div>}
          </CardContent>
        </Card>
      </section>
    </main>
  );
}

export default function LoginPage() {
  return <Suspense fallback={<div className="min-h-screen bg-slate-50" />}><LoginForm /></Suspense>;
}
