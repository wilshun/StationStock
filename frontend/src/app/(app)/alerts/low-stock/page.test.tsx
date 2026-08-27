import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import LowStockPage from "./page";
vi.mock("@/lib/hooks/use-api-query",()=>({useApiQuery:(path:string)=>({loading:false,error:null,reload:vi.fn(),data:path.startsWith("/alerts")?{items:[{product_id:"p1",sku:"DRINK-1",name:"Sparkling Water",category:{id:"c",name:"Drinks"},preferred_vendor:null,latest_quantity:2,latest_count_at:"2026-01-01T12:00:00Z",minimum_quantity:5,target_quantity:12,recommended_reorder_quantity:10}],page:1,pages:1,total:1}:{items:[]}})}));
describe("LowStockPage",()=>{it("renders backend quantities and explains uncounted exclusion",()=>{render(<LowStockPage/>);expect(screen.getByText("Sparkling Water")).toBeVisible();expect(screen.getByText("10")).toBeVisible();expect(screen.getByText(/Uncounted products are excluded/)).toBeVisible()})});
