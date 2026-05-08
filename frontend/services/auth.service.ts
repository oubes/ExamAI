interface AuthResponse {
  access_token?: string;
  message?: string;
  detail?: any;
}

const extractErrorMessage = (data: any, fallback: string) => {
  return (
    data?.detail?.message ||
    data?.detail ||
    data?.message ||
    (typeof data?.detail === "string" ? data.detail : null) ||
    fallback
  );
};

export const authService = {
  // ---- Login ----
  login: async (email: string, password: string): Promise<AuthResponse> => {
    const res = await fetch("http://127.0.0.1:8000/api/v1/identity/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });

    const data = await res.json().catch(() => ({}));

    if (!res.ok) {
      throw new Error(
        extractErrorMessage(data, "Login failed")
      );
    }

    return data;
  },

  // ---- Register ----
  register: async (payload: {
    full_name: string;
    email: string;
    password: string;
    user_name: string;
  }): Promise<AuthResponse> => {
    const res = await fetch("http://127.0.0.1:8000/api/v1/identity/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const data = await res.json().catch(() => ({}));

    if (!res.ok) {
      throw new Error(
        extractErrorMessage(data, "Registration failed")
      );
    }

    return data;
  },

  // ---- Reset Password ----
  resetPassword: async (email: string): Promise<AuthResponse> => {
    const url = `http://127.0.0.1:8000/api/v1/identity/reset-password/request?email=${encodeURIComponent(email)}`;

    const res = await fetch(url, {
      method: "POST",
      headers: { accept: "application/json" },
    });

    const data = await res.json().catch(() => ({}));

    if (!res.ok) {
      throw new Error(
        extractErrorMessage(data, "Reset password request failed")
      );
    }

    return data;
  },
};