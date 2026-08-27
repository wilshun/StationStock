"use client";
import { zodResolver } from "@hookform/resolvers/zod";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { Controller, useForm } from "react-hook-form";
import { toast } from "sonner";
import { z } from "zod";
import { ErrorState, LoadingState } from "@/components/shared/async-state";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { apiFetch, ApiError } from "@/lib/api/client";
import type { Category, Page, Product, ProductInput, Vendor } from "@/lib/api/types";
import { useApiQuery } from "@/lib/hooks/use-api-query";
const schema = z.object({ sku:z.string().trim().min(1,"SKU is required"), name:z.string().trim().min(1,"Name is required"), description:z.string(), unit_description:z.string(), category_id:z.string().min(1,"Category is required"), preferred_vendor_id:z.string(), minimum_quantity:z.number().int().min(0), target_quantity:z.number().int().min(0), is_active:z.boolean() }).refine(v=>v.target_quantity>=v.minimum_quantity,{path:["target_quantity"],message:"Target must be at least the minimum"});
type Values=z.infer<typeof schema>;
export function ProductForm({product}:{product?:Product}) {
 const router=useRouter(); const categories=useApiQuery<Page<Category>>("/categories?page_size=100&is_active=true"); const vendors=useApiQuery<Page<Vendor>>("/vendors?page_size=100&is_active=true");
 const form=useForm<Values>({resolver:zodResolver(schema),defaultValues:{sku:"",name:"",description:"",unit_description:"",category_id:"",preferred_vendor_id:"",minimum_quantity:0,target_quantity:0,is_active:true}});
 useEffect(()=>{if(product)form.reset({sku:product.sku,name:product.name,description:product.description??"",unit_description:product.unit_description??"",category_id:product.category.id,preferred_vendor_id:product.preferred_vendor?.id??"",minimum_quantity:product.minimum_quantity,target_quantity:product.target_quantity,is_active:product.is_active})},[product,form]);
 async function submit(v:Values){form.clearErrors("root");const payload:ProductInput&{is_active?:boolean}={...v,description:v.description||null,unit_description:v.unit_description||null,preferred_vendor_id:v.preferred_vendor_id||null};if(!product)delete payload.is_active;try{const saved=await apiFetch<Product>(product?`/products/${product.id}`:"/products",{method:product?"PATCH":"POST",body:payload});toast.success(product?"Product updated":"Product created");router.push(`/products/${saved.id}`)}catch(e){form.setError("root",{message:e instanceof ApiError?e.message:"Unable to save product"})}}
 if(categories.loading||vendors.loading)return <LoadingState/>;if(categories.error||vendors.error)return <ErrorState message={categories.error?.message??vendors.error?.message??"Unable to load form options"}/>;
 return <Card className="max-w-3xl"><CardContent className="p-6"><form onSubmit={form.handleSubmit(submit)} className="grid gap-5 sm:grid-cols-2">
 <Field label="SKU" error={form.formState.errors.sku?.message}><Input {...form.register("sku")} autoComplete="off"/></Field><Field label="Name" error={form.formState.errors.name?.message}><Input {...form.register("name")}/></Field>
 <Field label="Category" error={form.formState.errors.category_id?.message}><Controller control={form.control} name="category_id" render={({field})=><Select value={field.value} onValueChange={v=>field.onChange(v??"")}><SelectTrigger className="w-full"><SelectValue placeholder="Choose category"/></SelectTrigger><SelectContent>{categories.data?.items.map(i=><SelectItem key={i.id} value={i.id}>{i.name}</SelectItem>)}</SelectContent></Select>}/></Field>
 <Field label="Preferred vendor"><Controller control={form.control} name="preferred_vendor_id" render={({field})=><Select value={field.value||"none"} onValueChange={v=>field.onChange(v==="none"?"":v)}><SelectTrigger className="w-full"><SelectValue/></SelectTrigger><SelectContent><SelectItem value="none">None</SelectItem>{vendors.data?.items.map(i=><SelectItem key={i.id} value={i.id}>{i.name}</SelectItem>)}</SelectContent></Select>}/></Field>
 <Field label="Unit description"><Input {...form.register("unit_description")} placeholder="e.g. case of 24"/></Field><div/>
 <Field label="Minimum quantity" error={form.formState.errors.minimum_quantity?.message}><Input {...form.register("minimum_quantity",{valueAsNumber:true})} type="number" min="0" inputMode="numeric"/></Field><Field label="Target quantity" error={form.formState.errors.target_quantity?.message}><Input {...form.register("target_quantity",{valueAsNumber:true})} type="number" min="0" inputMode="numeric"/></Field>
 <div className="sm:col-span-2"><Field label="Description"><Textarea {...form.register("description")} rows={4}/></Field></div>{product&&<label className="flex items-center gap-3 sm:col-span-2"><Controller control={form.control} name="is_active" render={({field})=><Checkbox checked={field.value} onCheckedChange={field.onChange}/>}/><span>Active product</span></label>}
 {form.formState.errors.root&&<p role="alert" className="text-sm text-red-700 sm:col-span-2">{form.formState.errors.root.message}</p>}<div className="flex gap-3 sm:col-span-2"><Button type="submit" disabled={form.formState.isSubmitting}>{form.formState.isSubmitting?"Saving…":"Save product"}</Button><Button type="button" variant="outline" onClick={()=>router.back()}>Cancel</Button></div>
 </form></CardContent></Card>
}
function Field({label,error,children}:{label:string;error?:string;children:React.ReactNode}){return <div className="space-y-2"><Label className="flex flex-col items-stretch gap-2">{label}{children}</Label>{error&&<p role="alert" className="text-sm text-red-700">{error}</p>}</div>}
