import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import DashboardPage from "./page";
vi.mock("@/lib/hooks/use-api-query",()=>({useApiQuery:()=>({loading:false,error:null,reload:vi.fn(),data:{active_product_count:12,low_stock_product_count:2,uncounted_active_product_count:3,active_category_count:4,active_vendor_count:5,total_submitted_count_sessions:6,recent_submitted_count_sessions:[],prioritized_low_stock:[]}})}));
describe("Dashboard",()=>{it("renders real summary values including zero-length states",()=>{render(<DashboardPage/>);expect(screen.getByText("12")).toBeVisible();expect(screen.getByText("No low-stock products")).toBeVisible();expect(screen.getByText("No submitted counts")).toBeVisible()})});
