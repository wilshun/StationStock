import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

export function ActiveBadge({ active }: { active: boolean }) {
  return <Badge variant="outline" className={cn(active ? "border-emerald-200 bg-emerald-50 text-emerald-800" : "border-slate-300 bg-slate-100 text-slate-700")}>{active ? "Active" : "Inactive"}</Badge>;
}

export function CountStatusBadge({ status }: { status: "draft" | "submitted" }) {
  return <Badge variant="outline" className={status === "draft" ? "border-amber-200 bg-amber-50 text-amber-800" : "border-emerald-200 bg-emerald-50 text-emerald-800"}>{status === "draft" ? "Draft" : "Submitted"}</Badge>;
}

export function StockBadge({ low, counted }: { low: boolean | null; counted: boolean }) {
  if (!counted) return <Badge variant="outline" className="border-violet-200 bg-violet-50 text-violet-800">Uncounted</Badge>;
  return <Badge variant="outline" className={low ? "border-red-200 bg-red-50 text-red-800" : "border-emerald-200 bg-emerald-50 text-emerald-800"}>{low ? "Low stock" : "Stocked"}</Badge>;
}

export function RoleBadge({ role }: { role: "manager" | "employee" }) {
  return <Badge variant="outline" className={role === "manager" ? "border-blue-200 bg-blue-50 text-blue-800" : "border-slate-300 bg-slate-50 text-slate-700"}>{role === "manager" ? "Manager" : "Employee"}</Badge>;
}
