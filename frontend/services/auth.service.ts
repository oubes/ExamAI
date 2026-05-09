import api from "@/lib/api";

// ---- Types ----
interface AuthResponse {
  access_token?: string;
  refresh_token?: string;
  message?: string;
  detail?: any;
}

// ---- Helpers ----
const extractErrorMessage = (data: any, fallback: string): string => {
  // Handles FastAPI Pydantic validation errors (Array of objects)
  if (Array.isArray(data?.detail)) {
    return data.detail
      .map((err: any) => {
        const field = err.loc ? err.loc[err.loc.length - 1] : "field";
        return `${field}: ${err.msg || err.message}`;
      })
      .join(", ");
  }

  // Handles string detail or nested message objects
  return (
    data?.detail?.message ||
    (typeof data?.detail === "string" ? data.detail : null) ||
    data?.message ||
    fallback
  );
};

// ---- Auth Service ----
export const authService = {
  // ---- Login ----
  login: async (email: string, password: string): Promise<AuthResponse> => {
    try {
      const res = await api.post("/identity/login", {
        email,
        password,
      });

      return res.data;
    } catch (error: any) {
      const data = error.response?.data;
      throw new Error(extractErrorMessage(data, "Login failed"));
    }
  },

  // ---- Register ----
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

  // ---- Reset Password Request ----
  resetPassword: async (email: string): Promise<AuthResponse> => {
    try {
      const res = await api.post("/identity/reset-password/request", null, {
        params: { email },
        headers: {
          accept: "application/json",
        },
      });

      return res.data;
    } catch (error: any) {
      const data = error.response?.data;
      throw new Error(extractErrorMessage(data, "Reset password request failed"));
    }
  },

  // ---- Reset Redirect Handler ----
  handleResetRedirect: (token: string | null): string | null => {
    if (!token) return null;

    sessionStorage.setItem("reset_token", token);

    return token;
  },

  // ---- Confirm Reset Password ----
  confirmResetPassword: async (
    token: string,
    new_password: string
  ): Promise<AuthResponse> => {
    try {
      // Sending JSON body to match FastAPI Pydantic schema
      const res = await api.post("/identity/reset-password/confirm", {
        token,
        new_password,
      });

      return res.data;
    } catch (error: any) {
      const data = error.response?.data;
      throw new Error(extractErrorMessage(data, "Password reset failed"));
    }
  },

  // ---- Token Refresh ----
  refresh: async (): Promise<AuthResponse> => {
    try {
      const refreshToken = localStorage.getItem("refresh_token");

      if (!refreshToken) {
        throw new Error("No refresh token found");
      }

      const res = await api.post("/identity/refresh", {
        refresh_token: refreshToken,
      });

      if (res.data?.access_token) {
        localStorage.setItem("access_token", res.data.access_token);
      }

      if (res.data?.refresh_token) {
        localStorage.setItem("refresh_token", res.data.refresh_token);
      }

      return res.data;
    } catch (error: any) {
      const data = error.response?.data;

      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");

      throw new Error(extractErrorMessage(data, "Session expired"));
    }
  },

  // ---- Logout ----
  logout: async (): Promise<AuthResponse> => {
    try {
      const refreshToken = localStorage.getItem("refresh_token");

      const res = await api.post("/identity/logout", {
        refresh_token: refreshToken,
      });

      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");

      return res.data;
    } catch (error: any) {
      const data = error.response?.data;

      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");

      throw new Error(extractErrorMessage(data, "Logout failed"));
    }
  },
};