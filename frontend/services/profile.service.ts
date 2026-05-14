import api from "@/lib/api";


// ---- Types ----
interface ProfileResponse {
  id: string;

  full_name: string;
  user_name: string;
  email: string;

  role: string;

  is_active: boolean;
  is_verified: boolean;

  global_learning_velocity: number;
  preferred_difficulty_band: number;
}


interface ProfileUpdatePayload {
  full_name?: string;
  user_name?: string;
  email?: string;

  password_hash?: string;

  preferred_difficulty_band?: number;
}


interface PublicProfileResponse {
  id: string;

  full_name: string;
  user_name: string;

  global_learning_velocity: number;
  preferred_difficulty_band: number;

  is_verified: boolean;
}


interface ProfileStatsResponse {
  attempts: number;
  enrollments: number;
}


// ---- Helpers ----
const extractErrorMessage = (
  data: any,
  fallback: string
): string => {

  // ---- FastAPI Validation Errors ----
  if (Array.isArray(data?.detail)) {

    return data.detail
      .map((err: any) => {

        const field = err.loc
          ? err.loc[err.loc.length - 1]
          : "field";

        return `${field}: ${err.msg || err.message}`;
      })
      .join(", ");
  }

  // ---- Standard Errors ----
  return (
    data?.detail?.message ||
    (typeof data?.detail === "string"
      ? data.detail
      : null) ||
    data?.message ||
    fallback
  );
};


// ---- Profile Service ----
export const profileService = {

  // ---- Get My Profile ----
  getMyProfile: async (): Promise<ProfileResponse> => {

    try {

      const res = await api.get(
        "/profile/me"
      );

      return res.data;

    } catch (error: any) {

      const data = error.response?.data;

      throw new Error(
        extractErrorMessage(
          data,
          "Failed to fetch profile"
        )
      );
    }
  },


  // ---- Update My Profile ----
  updateMyProfile: async (
    payload: ProfileUpdatePayload
  ): Promise<ProfileResponse> => {

    try {

      const res = await api.put(
        "/profile/me",
        payload,
      );

      return res.data;

    } catch (error: any) {

      const data = error.response?.data;

      throw new Error(
        extractErrorMessage(
          data,
          "Failed to update profile"
        )
      );
    }
  },


  // ---- Get Public Profile ----
  getPublicProfile: async (
    userName: string
  ): Promise<PublicProfileResponse> => {

    try {

      const res = await api.get(
        `/profile/public/${userName}`
      );

      return res.data;

    } catch (error: any) {

      const data = error.response?.data;

      throw new Error(
        extractErrorMessage(
          data,
          "Failed to fetch public profile"
        )
      );
    }
  },


  // ---- Get Profile Stats ----
  getProfileStats: async (): Promise<ProfileStatsResponse> => {

    try {

      const res = await api.get(
        "/profile/stats/me"
      );

      return res.data;

    } catch (error: any) {

      const data = error.response?.data;

      throw new Error(
        extractErrorMessage(
          data,
          "Failed to fetch profile stats"
        )
      );
    }
  },
};