import api from "@/lib/api";

// -------------------- Base -------------------- //
const BASE = "/education/topics";

// -------------------- Types -------------------- //

export interface TopicPayload {
  title: string;
  description: string;
  chapter_id: string;
  is_active: boolean;
}

export interface TopicResponse {
  id: string;
  title: string;
  description: string;
  chapter_id: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ListTopicsResponse {
  items: TopicResponse[];
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

export const topicService = {
  listTopics: () =>
    safeApi<ListTopicsResponse>(
      () => api.get(`${BASE}`),
      "Failed to fetch topics"
    ),

  getTopic: (id: string) =>
    safeApi<TopicResponse>(
      () => api.get(`${BASE}/${id}`),
      "Failed to fetch topic"
    ),

  addTopic: (payload: TopicPayload) =>
    safeApi<TopicResponse>(
      () => api.post(`${BASE}`, payload),
      "Failed to add topic"
    ),

  updateTopic: (id: string, payload: Partial<TopicPayload>) =>
    safeApi<TopicResponse>(
      () => api.put(`${BASE}/${id}`, payload),
      "Failed to update topic"
    ),

  deleteTopic: (id: string) =>
    safeApi<DeleteResponse>(
      () => api.delete(`${BASE}/${id}`),
      "Failed to delete topic"
    ),
};