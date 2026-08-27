import { Button } from "@/components/ui/button";

export function PaginationControls({ page, pages, total, onPageChange }: { page: number; pages: number; total: number; onPageChange: (page: number) => void }) {
  if (!total) return null;
  return <div className="mt-5 flex flex-col gap-3 border-t border-slate-200 pt-4 text-sm text-slate-600 sm:flex-row sm:items-center sm:justify-between"><p>{total} total · Page {page} of {pages}</p><div className="flex gap-2"><Button variant="outline" disabled={page <= 1} onClick={() => onPageChange(page - 1)}>Previous</Button><Button variant="outline" disabled={page >= pages} onClick={() => onPageChange(page + 1)}>Next</Button></div></div>;
}
