import { afterEach, describe, expect, it, vi } from "vitest";
import { apiFetch, ApiError } from "./client";
describe("apiFetch",()=>{
 afterEach(()=>vi.restoreAllMocks());
 it("sends JSON with credentials",async()=>{const fetchMock=vi.spyOn(globalThis,"fetch").mockResolvedValue(new Response(JSON.stringify({ok:true}),{status:200,headers:{"Content-Type":"application/json"}}));await apiFetch("/test",{method:"POST",body:{name:"Fuel"}});expect(fetchMock).toHaveBeenCalledWith(expect.stringContaining("/test"),expect.objectContaining({credentials:"include",body:JSON.stringify({name:"Fuel"})}))});
 it("parses backend conflicts",async()=>{vi.spyOn(globalThis,"fetch").mockResolvedValue(new Response(JSON.stringify({detail:"Product SKU already exists"}),{status:409}));try{await apiFetch("/products");expect.fail("request should fail")}catch(error){expect(error).toBeInstanceOf(ApiError);expect((error as ApiError).status).toBe(409);expect((error as ApiError).message).toBe("Product SKU already exists")}});
 it("preserves validation details",async()=>{vi.spyOn(globalThis,"fetch").mockResolvedValue(new Response(JSON.stringify({detail:[{loc:["body","name"],msg:"Required",type:"missing"}]}),{status:422}));try{await apiFetch("/x");expect.fail("request should fail")}catch(error){expect((error as ApiError).validationErrors[0].loc).toEqual(["body","name"])}});
 it("returns a safe failed-login message",async()=>{vi.spyOn(globalThis,"fetch").mockResolvedValue(new Response(JSON.stringify({detail:"Invalid email or password"}),{status:401}));await expect(apiFetch("/auth/login",{method:"POST",body:{email:"x",password:"bad"}})).rejects.toMatchObject({status:401,message:"Invalid email or password"})});
});
