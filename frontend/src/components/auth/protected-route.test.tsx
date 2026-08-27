import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ProtectedRoute } from "./protected-route";
let state:{user:object|null;loading:boolean}={user:null,loading:true};
vi.mock("./auth-provider",()=>({useAuth:()=>state}));
describe("ProtectedRoute",()=>{it("does not flash protected content while loading",()=>{state={user:null,loading:true};render(<ProtectedRoute>secret</ProtectedRoute>);expect(screen.queryByText("secret")).not.toBeInTheDocument();expect(screen.getByLabelText("Loading account")).toBeVisible()});it("renders for an authenticated user",()=>{state={user:{id:"1"},loading:false};render(<ProtectedRoute>secret</ProtectedRoute>);expect(screen.getByText("secret")).toBeVisible()})});
