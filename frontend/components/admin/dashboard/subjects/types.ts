// ---- Types ----
export interface Subject {
  id: string;
  title: string;
  code: string;
  description: string;
  is_active: boolean;
  is_deleted?: boolean;
  created_at?: string;
  updated_at?: string;
}

export type FilterStatus = "all" | "active" | "deleted";