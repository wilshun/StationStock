"use client";
import { Plus } from "lucide-react";
import Link from "next/link";
import { useState } from "react";
import { EmptyState, ErrorState, LoadingState } from "@/components/shared/async-state";
import { PageHeader } from "@/components/shared/page-header";
import { PaginationControls } from "@/components/shared/pagination-controls";
import { CountStatusBadge } from "@/components/shared/status-badges";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { queryString } from "@/lib/api/client";
import type { InventoryCountListItem, Page } from "@/lib/api/types";
import { formatDate, shortId } from "@/lib/format";
import { useApiQuery } from "@/lib/hooks/use-api-query";
export default function CountsPage(){const[page,setPage]=useState(1),[status,setStatus]=useState("all"),[from,setFrom]=useState(""),[to,setTo]=useState("");const path=`/inventory-counts${queryString({page,page_size:20,status:status==="all"?null:status,date_from:from?new Date(from).toISOString():null,date_to:to?new Date(`${to}T23:59:59`).toISOString():null})}`;const q=useApiQuery<Page<InventoryCountListItem>>(path);return <><PageHeader title="Inventory counts" description="Review submitted sessions and resume saved drafts." actions={<Button render={<Link href="/inventory-counts/new"/>}><Plus/>Start count</Button>}/><Card className="mb-5"><CardContent className="grid gap-4 p-4 sm:grid-cols-3"><div><Label>Status</Label><Select value={status} onValueChange={v=>setStatus(v??"all")}><SelectTrigger className="w-full"><SelectValue/></SelectTrigger><SelectContent><SelectItem value="all">All statuses</SelectItem><SelectItem value="draft">Draft</SelectItem><SelectItem value="submitted">Submitted</SelectItem></SelectContent></Select></div><div><Label htmlFor="date-from">From</Label><Input id="date-from" type="date" value={from} onChange={e=>setFrom(e.target.value)}/></div><div><Label htmlFor="date-to">To</Label><Input id="date-to" type="date" value={to} onChange={e=>setTo(e.target.value)}/></div></CardContent></Card>{q.loading?<LoadingState/>:q.error?<ErrorState message={q.error.message} retry={q.reload}/>:!q.data?.items.length?<EmptyState title="No inventory counts" description="Start a count to record official inventory."/>:<><div className="grid gap-3">{q.data.items.map(c=><Link key={c.id} href={`/inventory-counts/${c.id}`} className="rounded-xl border bg-white p-5 transition hover:border-emerald-400"><div className="flex flex-wrap items-center justify-between gap-3"><div><p className="font-semibold">Count {shortId(c.id)}</p><p className="text-sm text-slate-600">Started by {c.started_by.full_name} · {formatDate(c.created_at)}</p></div><CountStatusBadge status={c.status}/></div><div className="mt-3 flex gap-6 text-sm"><span><strong>{c.item_count}</strong> items</span><span>{c.submitted_at?`Submitted ${formatDate(c.submitted_at)}`:"Saved draft"}</span></div></Link>)}</div><PaginationControls page={q.data.page} pages={q.data.pages} total={q.data.total} onPageChange={n=>{setPage(n);q.reload()}}/></>}</>}
