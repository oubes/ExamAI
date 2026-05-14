import api from "@/lib/api";

// -------------------- Base -------------------- //
const BASE = "/education/chapters";

// -------------------- Types -------------------- //

export interface ChapterPayload {
  title: string;
  description: string;
  subject_id: string;
  is_active: boolean;
}

export interface ChapterResponse {
  id: string;
  title: string;
  description: string;
  subject_id: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ListChaptersResponse {
  items: ChapterResponse[];
}

export interface DeleteResponse {
  success: boolean;
}

// -------------------- Error Handler -------------------- //

const extractErrorMessage = (data: any, fallback: string): string => {
  if (Array.isArray(data?.detail)) {
    return data.detail
      .map((err: any) => {
        const field = err.loc?.at?.(-1) ?? err.loc?.[err.loc.length - 1] ?? "field";
        return `${field}: ${err.msg || err.message}`;
      })
      .join(", ");
  }

  return data?.detail?.message ||
    (typeof data?.detail === "string" ? data.detail : null) ||
    data?.message ||
    fallback;
};

// -------------------- Safe API -------------------- //

const safeApi = async <T>(
  fn: () => Promise<{ data: T }>,
  fallback: string
): Promise<T> => {
  try {
    const res = await fn();
    return res.data;
  } catch (error: any) {
    throw new Error(
      extractErrorMessage(error.response?.data, fallback)
    );
  }
};

// -------------------- Service -------------------- //

export const chapterService = {
  listChapters: () =>
    safeApi<ListChaptersResponse>(
      () => api.get(`${BASE}`),
      "Failed to fetch chapters"
    ),

  getChapter: (id: string) =>
    safeApi<ChapterResponse>(
      () => api.get(`${BASE}/${id}`),
      "Failed to fetch chapter"
    ),

  addChapter: (payload: ChapterPayload) =>
    safeApi<ChapterResponse>(
      () => api.post(`${BASE}`, payload),
      "Failed to add chapter"
    ),

  updateChapter: (id: string, payload: Partial<ChapterPayload>) =>
    safeApi<ChapterResponse>(
      () => api.put(`${BASE}/${id}`, payload),
      "Failed to update chapter"
    ),

  deleteChapter: (id: string) =>
    safeApi<DeleteResponse>(
      () => api.delete(`${BASE}/${id}`),
      "Failed to delete chapter"
    ),
};