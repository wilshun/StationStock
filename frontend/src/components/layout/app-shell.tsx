"use client";

import { AlertTriangle, Boxes, ClipboardList, LayoutDashboard, LogOut, Menu, PackagePlus, Tags, Truck, Users } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";

import { useAuth } from "@/components/auth/auth-provider";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from "@/components/ui/sheet";
import { cn } from "@/lib/utils";

const baseNavigation = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/products", label: "Products", icon: Boxes },
  { href: "/inventory-counts", label: "Inventory counts", icon: ClipboardList },
  { href: "/alerts/low-stock", label: "Low stock", icon: AlertTriangle },
  { href: "/categories", label: "Categories", icon: Tags },
  { href: "/vendors", label: "Vendors", icon: Truck },
];

function Navigation({ onNavigate }: { onNavigate?: () => void }) {
  const pathname = usePathname();
  const { user } = useAuth();
  const links = user?.role === "manager"
    ? [...baseNavigation, { href: "/products/new", label: "Add product", icon: PackagePlus }, { href: "/users", label: "Users", icon: Users }]
    : baseNavigation;

  return (
    <nav aria-label="Main navigation" className="space-y-1">
      {links.map(({ href, label, icon: Icon }) => {
        const active = pathname === href || (href !== "/dashboard" && pathname.startsWith(`${href}/`));
        return (
          <Link key={href} href={href} onClick={onNavigate} className={cn("flex min-h-11 items-center gap-3 rounded-lg px-3 text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-600", active ? "bg-emerald-50 text-emerald-800" : "text-slate-600 hover:bg-slate-100 hover:text-slate-950")}>
            <Icon className="size-5" aria-hidden="true" />{label}
          </Link>
        );
      })}
    </nav>
  );
}

export function AppShell({ children }: { children: React.ReactNode }) {
  const { user, logout } = useAuth();
  return (
    <div className="min-h-screen bg-slate-50 text-slate-950">
      <aside className="fixed inset-y-0 left-0 z-30 hidden w-64 border-r border-slate-200 bg-white p-5 lg:flex lg:flex-col">
        <Link href="/dashboard" className="mb-8 flex items-center gap-3 rounded-lg focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-600">
          <span className="grid size-10 place-items-center rounded-xl bg-slate-900 font-bold text-white">SS</span>
          <span><span className="block font-semibold">StationStock</span><span className="block text-xs text-slate-500">Inventory operations</span></span>
        </Link>
        <Navigation />
        <div className="mt-auto border-t border-slate-200 pt-4">
          <p className="truncate text-sm font-medium">{user?.email}</p>
          <Badge variant="secondary" className="mt-2 capitalize">{user?.role}</Badge>
          <Button variant="ghost" className="mt-3 w-full justify-start" onClick={() => void logout()}><LogOut className="size-4" /> Logout</Button>
        </div>
      </aside>
      <header className="sticky top-0 z-20 flex h-16 items-center justify-between border-b border-slate-200 bg-white/95 px-4 backdrop-blur lg:ml-64 lg:px-8">
        <div className="flex items-center gap-3">
          <Sheet>
            <SheetTrigger render={<Button variant="outline" size="icon" className="lg:hidden" aria-label="Open navigation" />}><Menu className="size-5" /></SheetTrigger>
            <SheetContent side="left" className="w-72 p-5"><SheetHeader className="mb-6 text-left"><SheetTitle>StationStock</SheetTitle></SheetHeader><Navigation /></SheetContent>
          </Sheet>
          <p className="font-semibold lg:hidden">StationStock</p>
        </div>
        <div className="text-right lg:hidden"><p className="max-w-48 truncate text-sm font-medium">{user?.email}</p><p className="text-xs capitalize text-slate-500">{user?.role}</p></div>
      </header>
      <main className="px-4 py-6 sm:px-6 lg:ml-64 lg:px-8 lg:py-8"><div className="mx-auto max-w-7xl">{children}</div></main>
    </div>
  );
}
