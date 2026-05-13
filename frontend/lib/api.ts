import axios, {
  AxiosError,
  InternalAxiosRequestConfig,
} from "axios";

// ---------- Extended Axios Config ----------
interface CustomAxiosRequestConfig
  extends InternalAxiosRequestConfig {
  _retry?: boolean;
}

// ---------- API Base URL ----------
const BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  "http://127.0.0.1:8000/api/v1";

// ---------- API Instance ----------
const api = axios.create({
  baseURL: BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// ---------- Attach Access Token ----------
api.interceptors.request.use(
  (config) => {
    if (typeof window === "undefined") return config;

    const token = localStorage.getItem("access_token");

    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    if (
      typeof FormData !== "undefined" &&
      config.data instanceof FormData
    ) {
      delete (config.headers as any)?.["Content-Type"];
    }

    return config;
  },
  (error) => Promise.reject(error)
);

// ---------- Response Interceptor ----------
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest =
      error.config as CustomAxiosRequestConfig;

    if (!originalRequest || typeof window === "undefined") {
      return Promise.reject(error);
    }

    const isRefreshRequest =
      originalRequest.url?.includes("/identity/refresh");

    if (
      error.response?.status === 401 &&
      !originalRequest._retry &&
      !isRefreshRequest
    ) {
      originalRequest._retry = true;

      const refreshToken =
        localStorage.getItem("refresh_token");

      if (!refreshToken) {
        localStorage.clear();
        window.location.href = "/AuthPage";
        return Promise.reject(error);
      }

      try {
        const refreshResponse = await axios.post(
          `${BASE_URL}/identity/refresh`,
          null,
          {
            headers: {
              Authorization: `Bearer ${refreshToken}`,
              "Content-Type": "application/json",
            },
          }
        );

        const {
          access_token,
          refresh_token: newRefreshToken,
        } = refreshResponse.data;

        if (!access_token) {
          throw new Error("Invalid refresh response");
        }

        localStorage.setItem("access_token", access_token);

        if (newRefreshToken) {
          localStorage.setItem("refresh_token", newRefreshToken);
        }

        if (originalRequest.headers) {
          originalRequest.headers.Authorization =
            `Bearer ${access_token}`;
        }

        return api(originalRequest);
      } catch (refreshError) {
        localStorage.clear();
        window.location.href = "/AuthPage";
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default api;