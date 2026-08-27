import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { AppShell } from "./app-shell";
let role:"manager"|"employee"="employee";
vi.mock("@/components/auth/auth-provider",()=>({useAuth:()=>({user:{email:"person@example.com",role},logout:vi.fn()})}));
describe("role-aware navigation",()=>{it("hides administrative routes from employees",()=>{role="employee";render(<AppShell>content</AppShell>);expect(screen.queryByText("Users")).not.toBeInTheDocument();expect(screen.queryByText("Add product")).not.toBeInTheDocument()});it("shows administrative routes to managers",()=>{role="manager";render(<AppShell>content</AppShell>);expect(screen.getAllByText("Users").length).toBeGreaterThan(0);expect(screen.getAllByText("Add product").length).toBeGreaterThan(0)})});
