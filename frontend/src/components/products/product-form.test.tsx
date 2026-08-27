import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { ProductForm } from "./product-form";
vi.mock("@/lib/hooks/use-api-query",()=>({useApiQuery:(path:string)=>({loading:false,error:null,data:{items:path.startsWith("/categories")?[{id:"cat",name:"Fuel"}]:[{id:"vendor",name:"Supplier"}]}})}));
describe("ProductForm",()=>{it("requires identity and enforces target at least minimum",async()=>{render(<ProductForm/>);await userEvent.clear(screen.getByLabelText("Minimum quantity"));await userEvent.type(screen.getByLabelText("Minimum quantity"),"10");await userEvent.clear(screen.getByLabelText("Target quantity"));await userEvent.type(screen.getByLabelText("Target quantity"),"5");await userEvent.click(screen.getByRole("button",{name:"Save product"}));expect(await screen.findByText("SKU is required")).toBeVisible();expect(screen.getByText("Target must be at least the minimum")).toBeVisible()})});
