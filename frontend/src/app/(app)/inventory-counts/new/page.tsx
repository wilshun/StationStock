"use client";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { PageHeader } from "@/components/shared/page-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { apiFetch, ApiError } from "@/lib/api/client";
import type { InventoryCount } from "@/lib/api/types";
export default function NewCountPage(){const router=useRouter();const[notes,setNotes]=useState(""),[busy,setBusy]=useState(false),[error,setError]=useState("");async function start(){setBusy(true);setError("");try{const count=await apiFetch<InventoryCount>("/inventory-counts",{method:"POST",body:{notes:notes||null}});router.push(`/inventory-counts/${count.id}`)}catch(e){setError(e instanceof ApiError?e.message:"Unable to start count");setBusy(false)}}return <><PageHeader title="Start inventory count" description="Create a saved draft, then enter quantities for the products you count."/><Card className="max-w-2xl"><CardContent className="space-y-5 p-6"><div><Label htmlFor="count-notes">Notes (optional)</Label><Textarea id="count-notes" value={notes} onChange={e=>setNotes(e.target.value)} placeholder="Shift, location, or context for this count"/></div>{error&&<p role="alert" className="text-sm text-red-700">{error}</p>}<Button onClick={start} disabled={busy}>{busy?"Starting…":"Start count"}</Button></CardContent></Card></>}
