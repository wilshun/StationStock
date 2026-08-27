"use client";
import { ManagerRoute } from "@/components/auth/manager-route";
import { ProductForm } from "@/components/products/product-form";
import { PageHeader } from "@/components/shared/page-header";
export default function NewProductPage(){return <ManagerRoute><PageHeader title="Add product" description="Create a catalog item and define its inventory thresholds."/><ProductForm/></ManagerRoute>}
