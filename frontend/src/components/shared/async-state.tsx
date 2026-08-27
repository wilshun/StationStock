import { AlertCircle, Inbox } from "lucide-react";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";

export function LoadingState({ rows = 4 }: { rows?: number }) {
  return <div className="space-y-3" aria-label="Loading"><Skeleton className="h-12 w-full" />{Array.from({ length: rows }).map((_, index) => <Skeleton key={index} className="h-20 w-full" />)}</div>;
}

export function ErrorState({ message, retry }: { message: string; retry?: () => void }) {
  return <Alert variant="destructive"><AlertCircle /><AlertTitle>Unable to load data</AlertTitle><AlertDescription className="flex flex-col items-start gap-3"><span>{message}</span>{retry && <Button variant="outline" size="sm" onClick={retry}>Try again</Button>}</AlertDescription></Alert>;
}

export function EmptyState({ title, description }: { title: string; description: string }) {
  return <div className="grid min-h-52 place-items-center rounded-xl border border-dashed border-slate-300 bg-white p-8 text-center"><div><Inbox className="mx-auto size-9 text-slate-400" /><h2 className="mt-3 font-semibold">{title}</h2><p className="mt-1 text-sm text-slate-500">{description}</p></div></div>;
}
