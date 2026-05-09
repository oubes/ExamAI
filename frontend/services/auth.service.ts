// ---- Custom API Instance Import ----
import api from "@/lib/api";

// ---- Types ----
interface AuthResponse {
  access_token?: string;
  refresh_token?: string;
  message?: string;
  detail?: any;
}

// ---- Error Extraction Utility ----
const extractErrorMessage = (data: any, fallback: string): string => {
  return (
    data?.detail?.message ||
    data?.detail ||
    data?.message ||
    (typeof data?.detail === "string" ? data.detail : null) ||
    fallback
  );
};

export const authService = {
  // ---- Identity: Login ----
  login: async (email: string, password: string): Promise<AuthResponse> => {
    try {
      const res = await api.post("/identity/login", { email, password });
      return res.data;
    } catch (error: any) {
      const data = error.response?.data;
      throw new Error(extractErrorMessage(data, "Login failed"));
    }
  },

  // ---- Identity: Register ----
  register: async (payload: {
    full_name: string;
    email: string;
    password: string;
    user_name: string;
  }): Promise<AuthResponse> => {
    try {
      const res = await api.post("/identity/register", payload);
      return res.data;
    } catch (error: any) {
      const data = error.response?.data;
      throw new Error(extractErrorMessage(data, "Registration failed"));
    }
  },

  // ---- Identity: Reset Password Request ----
  resetPassword: async (email: string): Promise<AuthResponse> => {
    try {
      const res = await api.post(`/identity/reset-password/request`, null, {
        params: { email: email },
        headers: { accept: "application/json" }
      });
      return res.data;
    } catch (error: any) {
      const data = error.response?.data;
      throw new Error(extractErrorMessage(data, "Reset password request failed"));
    }
  },
};