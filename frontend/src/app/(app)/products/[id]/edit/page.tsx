"use client";
import { useParams } from "next/navigation";
import { ManagerRoute } from "@/components/auth/manager-route";
import { ProductForm } from "@/components/products/product-form";
import { ErrorState, LoadingState } from "@/components/shared/async-state";
import { PageHeader } from "@/components/shared/page-header";
import type { Product } from "@/lib/api/types";
import { useApiQuery } from "@/lib/hooks/use-api-query";
export default function EditProductPage(){const{id}=useParams<{id:string}>();const q=useApiQuery<Product>(`/products/${id}`);return <ManagerRoute><PageHeader title="Edit product" description="Update catalog details and inventory thresholds."/><>{q.loading?<LoadingState/>:q.error||!q.data?<ErrorState message={q.error?.message??"Product not found"}/>:<ProductForm product={q.data}/>}</></ManagerRoute>}
