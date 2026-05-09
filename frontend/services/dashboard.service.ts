import api from "@/lib/api";

// ---- Types ----
export interface MeResponse {
  id: string;
  full_name: string;
  user_name: string;
  email: string;
  role: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// ---- Me Service ----
export const meService = {
  getMe: async (): Promise<MeResponse> => {
    const res = await api.get("/identity/me");
    return res.data;
  },
};