import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { MasterDataPage } from "./master-data-page";
const apiFetch=vi.fn();
vi.mock("@/lib/api/client",()=>({apiFetch:(...args:unknown[])=>apiFetch(...args),ApiError:class extends Error{},queryString:()=>""}));
vi.mock("@/components/auth/auth-provider",()=>({useAuth:()=>({user:{role:"manager"}})}));
vi.mock("@/lib/hooks/use-api-query",()=>({useApiQuery:()=>({loading:false,error:null,reload:vi.fn(),data:{items:[],page:1,pages:0,total:0}})}));
describe("category form",()=>{it("creates a named category through the API",async()=>{apiFetch.mockResolvedValue({});render(<MasterDataPage kind="categories"/>);await userEvent.click(screen.getByRole("button",{name:"Add categorie"}));const fields=within(screen.getByRole("dialog")).getAllByRole("textbox");await userEvent.type(fields[0],"Beverages");await userEvent.click(screen.getByRole("button",{name:"Save"}));await waitFor(()=>expect(apiFetch).toHaveBeenCalledWith("/categories",{method:"POST",body:{name:"Beverages",description:null}}))})});
