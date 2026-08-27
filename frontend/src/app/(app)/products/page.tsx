"use client";

import { Plus, Search } from "lucide-react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useState } from "react";

import { useAuth } from "@/components/auth/auth-provider";
import { EmptyState, ErrorState, LoadingState } from "@/components/shared/async-state";
import { PageHeader } from "@/components/shared/page-header";
import { PaginationControls } from "@/components/shared/pagination-controls";
import { ActiveBadge, StockBadge } from "@/components/shared/status-badges";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { queryString } from "@/lib/api/client";
import type { Category, Page, Product, Vendor } from "@/lib/api/types";
import { useApiQuery } from "@/lib/hooks/use-api-query";

function ProductList() {
  const router = useRouter();
  const params = useSearchParams();
  const { user } = useAuth();
  const [search, setSearch] = useState(params.get("search") ?? "");
  const page = Number(params.get("page") ?? 1);
  const path = `/products${queryString({ page, page_size: 20, search: params.get("search"), category_id: params.get("category_id"), preferred_vendor_id: params.get("preferred_vendor_id"), is_active: params.get("is_active"), is_counted: params.get("is_counted"), is_low_stock: params.get("is_low_stock") })}`;
  const products = useApiQuery<Page<Product>>(path);
  const categories = useApiQuery<Page<Category>>("/categories?page_size=100&is_active=true");
  const vendors = useApiQuery<Page<Vendor>>("/vendors?page_size=100&is_active=true");

  function updateParam(key: string, value: string) {
    const next = new URLSearchParams(params.toString());
    if (!value || value === "all") next.delete(key); else next.set(key, value);
    if (key !== "page") next.set("page", "1");
    router.replace(`/products?${next.toString()}`);
  }
  function submitSearch(event: React.FormEvent) { event.preventDefault(); updateParam("search", search.trim()); }

  return <div><PageHeader title="Products" description="Search the catalog and see official inventory from submitted counts." actions={user?.role === "manager" ? <Button render={<Link href="/products/new" />}><Plus /> Add product</Button> : undefined} />
    <Card className="mb-5 border-slate-200"><CardContent className="grid gap-4 p-4 md:grid-cols-2 xl:grid-cols-7">
      <form onSubmit={submitSearch} className="flex gap-2 md:col-span-2"><div className="flex-1"><Label htmlFor="product-search" className="sr-only">Search products</Label><Input id="product-search" value={search} onChange={event => setSearch(event.target.value)} placeholder="Search name or SKU" /></div><Button type="submit" variant="outline"><Search /> Search</Button></form>
      <Filter label="Category" value={params.get("category_id") ?? "all"} onChange={value => updateParam("category_id", value)} options={categories.data?.items.map(item => [item.id, item.name]) ?? []} />
      <Filter label="Vendor" value={params.get("preferred_vendor_id") ?? "all"} onChange={value => updateParam("preferred_vendor_id", value)} options={vendors.data?.items.map(item => [item.id, item.name]) ?? []} />
      <Filter label="Count state" value={params.get("is_counted") ?? "all"} onChange={value => updateParam("is_counted", value)} options={[["true", "Counted"], ["false", "Uncounted"]]} />
      <Filter label="Stock state" value={params.get("is_low_stock") ?? "all"} onChange={value => updateParam("is_low_stock", value)} options={[["true", "Low stock"], ["false", "Adequate"]]} />
      <Filter label="Active state" value={params.get("is_active") ?? "all"} onChange={value => updateParam("is_active", value)} options={[["true", "Active"], ["false", "Inactive"]]} />
    </CardContent></Card>
    {products.loading ? <LoadingState /> : products.error ? <ErrorState message={products.error.message} retry={products.reload} /> : !products.data?.items.length ? <EmptyState title="No products found" description="Try adjusting the current search or filters." /> : <>
      <div className="grid gap-3 md:hidden">{products.data.items.map(product => <ProductCard key={product.id} product={product} manager={user?.role === "manager"} />)}</div>
      <div className="hidden overflow-hidden rounded-xl border border-slate-200 bg-white md:block"><Table><TableHeader><TableRow><TableHead>Product</TableHead><TableHead>Category</TableHead><TableHead>Vendor</TableHead><TableHead className="text-right">Quantity</TableHead><TableHead className="text-right">Min / Target</TableHead><TableHead>Status</TableHead><TableHead className="text-right">Reorder</TableHead></TableRow></TableHeader><TableBody>{products.data.items.map(product => <TableRow key={product.id}><TableCell><Link href={`/products/${product.id}`} className="font-medium hover:text-emerald-700 hover:underline">{product.name}</Link><p className="text-xs text-slate-500">{product.sku}</p></TableCell><TableCell>{product.category.name}</TableCell><TableCell>{product.preferred_vendor?.name ?? "—"}</TableCell><TableCell className="text-right font-medium">{product.latest_quantity ?? "Uncounted"}</TableCell><TableCell className="text-right">{product.minimum_quantity} / {product.target_quantity}</TableCell><TableCell><div className="flex flex-wrap gap-1"><StockBadge low={product.is_low_stock} counted={product.is_counted} /><ActiveBadge active={product.is_active} /></div></TableCell><TableCell className="text-right">{product.recommended_reorder_quantity ?? "—"}</TableCell></TableRow>)}</TableBody></Table></div>
      <PaginationControls page={products.data.page} pages={products.data.pages} total={products.data.total} onPageChange={next => updateParam("page", String(next))} />
    </>}
  </div>;
}

function Filter({ label, value, onChange, options }: { label: string; value: string; onChange: (value: string) => void; options: string[][] }) {
  return <div className="space-y-1"><Label>{label}</Label><Select value={value} onValueChange={value => value && onChange(value)}><SelectTrigger className="w-full"><SelectValue /></SelectTrigger><SelectContent><SelectItem value="all">All</SelectItem>{options.map(([id, name]) => <SelectItem key={id} value={id}>{name}</SelectItem>)}</SelectContent></Select></div>;
}

function ProductCard({ product, manager }: { product: Product; manager: boolean }) {
  return <Card className="border-slate-200"><CardContent className="p-4"><div className="flex items-start justify-between gap-3"><div><Link href={`/products/${product.id}`} className="font-semibold hover:underline">{product.name}</Link><p className="text-sm text-slate-500">{product.sku} · {product.category.name}</p></div><StockBadge low={product.is_low_stock} counted={product.is_counted} /></div><div className="mt-4 grid grid-cols-3 gap-2 text-sm"><div><p className="text-slate-500">On hand</p><p className="font-medium">{product.latest_quantity ?? "Uncounted"}</p></div><div><p className="text-slate-500">Target</p><p className="font-medium">{product.target_quantity}</p></div><div><p className="text-slate-500">Reorder</p><p className="font-medium">{product.recommended_reorder_quantity ?? "—"}</p></div></div>{manager && <Button render={<Link href={`/products/${product.id}/edit`} />} variant="outline" size="sm" className="mt-4">Edit</Button>}</CardContent></Card>;
}

export default function ProductsPage() { return <Suspense fallback={<LoadingState />}><ProductList /></Suspense>; }
