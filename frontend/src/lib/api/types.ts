export type UserRole = "manager" | "employee";
export type InventoryCountStatus = "draft" | "submitted";

export interface Page<T> {
  items: T[];
  page: number;
  page_size: number;
  total: number;
  pages: number;
}

export interface CurrentUser {
  id: string;
  email: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
}

export interface User extends CurrentUser {
  full_name: string;
  updated_at: string;
}

export interface Category {
  id: string;
  name: string;
  description: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface CategorySummary {
  id: string;
  name: string;
}

export interface Vendor {
  id: string;
  name: string;
  contact_name: string | null;
  phone: string | null;
  email: string | null;
  notes: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface VendorSummary {
  id: string;
  name: string;
}

export interface Product {
  id: string;
  sku: string;
  name: string;
  description: string | null;
  unit_description: string | null;
  minimum_quantity: number;
  target_quantity: number;
  is_active: boolean;
  category: CategorySummary;
  preferred_vendor: VendorSummary | null;
  latest_quantity: number | null;
  latest_count_at: string | null;
  is_counted: boolean;
  is_low_stock: boolean | null;
  recommended_reorder_quantity: number | null;
  created_at: string;
  updated_at: string;
}

export interface ProductHistoryItem {
  count_id: string;
  submitted_at: string;
  quantity: number;
  submitted_by_user_id: string;
  submitted_by_email: string;
}

export interface UserSummary {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
}

export interface ProductSummary {
  id: string;
  sku: string;
  name: string;
}

export interface InventoryCountItem {
  id: string;
  product: ProductSummary;
  quantity: number;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface InventoryCount {
  id: string;
  status: InventoryCountStatus;
  started_by: UserSummary;
  submitted_by: UserSummary | null;
  notes: string | null;
  submitted_at: string | null;
  created_at: string;
  updated_at: string;
  items: InventoryCountItem[];
}

export interface InventoryCountListItem extends Omit<InventoryCount, "items"> {
  item_count: number;
}

export interface LowStockItem {
  product_id: string;
  sku: string;
  name: string;
  category: CategorySummary;
  preferred_vendor: VendorSummary | null;
  latest_quantity: number;
  latest_count_at: string;
  minimum_quantity: number;
  target_quantity: number;
  recommended_reorder_quantity: number;
}

export interface RecentCountSummary {
  id: string;
  submitted_at: string;
  submitted_by: UserSummary;
  item_count: number;
}

export interface DashboardSummary {
  active_product_count: number;
  low_stock_product_count: number;
  uncounted_active_product_count: number;
  active_category_count: number;
  active_vendor_count: number;
  total_submitted_count_sessions: number;
  recent_submitted_count_sessions: RecentCountSummary[];
  prioritized_low_stock: LowStockItem[];
}

export interface ProductInput {
  sku: string;
  name: string;
  description?: string | null;
  unit_description?: string | null;
  category_id: string;
  preferred_vendor_id?: string | null;
  minimum_quantity: number;
  target_quantity: number;
  is_active?: boolean;
}

export interface ValidationErrorItem {
  loc: Array<string | number>;
  msg: string;
  type: string;
}
