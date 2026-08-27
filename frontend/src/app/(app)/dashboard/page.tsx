"use client";

import { AlertTriangle, Boxes, ClipboardCheck, PackageSearch, Tags, Truck } from "lucide-react";
import Link from "next/link";

import { EmptyState, ErrorState, LoadingState } from "@/components/shared/async-state";
import { PageHeader } from "@/components/shared/page-header";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useApiQuery } from "@/lib/hooks/use-api-query";
import type { DashboardSummary } from "@/lib/api/types";
import { formatDateTime, shortId } from "@/lib/format";

export default function DashboardPage() {
  const { data, loading, error, reload } = useApiQuery<DashboardSummary>("/dashboard/summary");
  if (loading) return <><PageHeader title="Dashboard" description="Your current inventory picture." /><LoadingState /></>;
  if (error || !data) return <><PageHeader title="Dashboard" /><ErrorState message={error?.message ?? "Dashboard data is unavailable."} retry={reload} /></>;
  const metrics = [
    ["Active products", data.active_product_count, Boxes, "text-sky-700"],
    ["Low stock", data.low_stock_product_count, AlertTriangle, "text-amber-700"],
    ["Uncounted", data.uncounted_active_product_count, PackageSearch, "text-violet-700"],
    ["Submitted counts", data.total_submitted_count_sessions, ClipboardCheck, "text-emerald-700"],
    ["Categories", data.active_category_count, Tags, "text-indigo-700"],
    ["Vendors", data.active_vendor_count, Truck, "text-cyan-700"],
  ] as const;
  return <div><PageHeader title="Dashboard" description="Official inventory is based only on submitted counts." />
    <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3" aria-label="Inventory summary">{metrics.map(([label, value, Icon, tone]) => <Card key={label} className="border-slate-200 shadow-sm"><CardHeader className="flex flex-row items-center justify-between pb-2"><CardTitle className="text-sm font-medium text-slate-600">{label}</CardTitle><Icon className={`size-5 ${tone}`} /></CardHeader><CardContent><p className="text-3xl font-semibold">{value}</p></CardContent></Card>)}</section>
    <section className="mt-6 grid gap-6 xl:grid-cols-[1.2fr_1fr]">
      <Card className="border-slate-200 shadow-sm"><CardHeader className="flex flex-row items-center justify-between"><CardTitle>Priority restocks</CardTitle><Link href="/alerts/low-stock" className="text-sm font-medium text-emerald-700 hover:underline">View all</Link></CardHeader><CardContent className="space-y-3">{data.prioritized_low_stock.length ? data.prioritized_low_stock.map(item => <Link key={item.product_id} href={`/products/${item.product_id}`} className="flex min-h-16 items-center justify-between rounded-xl border border-slate-200 p-4 hover:border-emerald-300"><div><p className="font-medium">{item.name}</p><p className="text-sm text-slate-500">{item.sku} · {item.latest_quantity} on hand</p></div><Badge variant="outline" className="border-amber-200 bg-amber-50 text-amber-800">Reorder {item.recommended_reorder_quantity}</Badge></Link>) : <EmptyState title="No low-stock products" description="Submitted counts are currently above minimums." />}</CardContent></Card>
      <Card className="border-slate-200 shadow-sm"><CardHeader><CardTitle>Recent counts</CardTitle></CardHeader><CardContent className="space-y-3">{data.recent_submitted_count_sessions.length ? data.recent_submitted_count_sessions.map(count => <Link key={count.id} href={`/inventory-counts/${count.id}`} className="block rounded-xl border border-slate-200 p-4 hover:border-emerald-300"><div className="flex justify-between gap-3"><p className="font-medium">Count {shortId(count.id)}</p><span className="text-sm text-slate-500">{count.item_count} items</span></div><p className="mt-1 text-sm text-slate-500">{count.submitted_by.email} · {formatDateTime(count.submitted_at)}</p></Link>) : <EmptyState title="No submitted counts" description="Submitted inventory sessions will appear here." />}</CardContent></Card>
    </section>
  </div>;
}
