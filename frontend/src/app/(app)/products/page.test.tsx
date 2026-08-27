import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import ProductsPage from "./page";
vi.mock("@/components/auth/auth-provider",()=>({useAuth:()=>({user:{role:"employee"}})}));
vi.mock("@/lib/hooks/use-api-query",()=>({useApiQuery:(path:string)=>({loading:false,error:null,reload:vi.fn(),data:path.startsWith("/products")?{items:[{id:"p1",sku:"NEW-1",name:"New Product",description:null,unit_description:null,minimum_quantity:2,target_quantity:8,is_active:true,category:{id:"c",name:"Other"},preferred_vendor:null,latest_quantity:null,latest_count_at:null,is_counted:false,is_low_stock:null,recommended_reorder_quantity:null,created_at:"",updated_at:""}],page:1,pages:2,total:21}:{items:[]}})}));
describe("ProductsPage",()=>{it("shows filter controls, null inventory, and pagination",()=>{render(<ProductsPage/>);expect(screen.getByPlaceholderText("Search name or SKU")).toBeVisible();expect(screen.getAllByText("Uncounted").length).toBeGreaterThan(0);expect(screen.getByText(/21 total/)).toBeVisible();expect(screen.getByRole("button",{name:/next/i})).toBeEnabled()})});
