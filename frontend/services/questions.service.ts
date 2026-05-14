import api from "@/lib/api";

// -------------------- Base -------------------- //
const BASE = "/question/question_generation";

// -------------------- Types -------------------- //

export interface Question {
  id: string;
  subject_id: string;
  chapter_id: string;
  topic_id: string;
  content: string;
  type: "mcq" | "written";
  difficulty: number;
  importance: number;
}

export interface QuestionOption {
  id: string;
  question_id: string;
  option_text: string;
  is_correct: boolean;
  order: number;
}

export interface ModelAnswer {
  id: string;
  question_id: string;
  answer_text: string;
}

export interface QuestionBundle {
  question: Question;
  options: QuestionOption[];
  model_answer: ModelAnswer | null;
}

export interface QuestionListQuery {
  subject_id?: string;
  chapter_id?: string;
  topic_id?: string;
  limit?: number;
  offset?: number;
}

// -------------------- IMPORTANT: FLAT UPDATE DTO -------------------- //
export interface QuestionBundleUpdateRequest {
  content?: string;
  explanation?: string;
  difficulty?: number;
  importance?: number;
  tags?: string;
  model_answer?: string;
  options?: QuestionOption[];
}

// -------------------- Response -------------------- //

export interface DeleteQuestionResponse {
  deleted: boolean;
}

// -------------------- Helpers -------------------- //

const extractErrorMessage = (data: any, fallback: string): string => {
  if (Array.isArray(data?.detail)) {
    return data.detail
      .map((err: any) => {
        const field = err.loc?.at(-1) ?? "field";
        return `${field}: ${err.msg || err.message}`;
      })
      .join(", ");
  }

  return data?.detail || data?.message || fallback;
};

// -------------------- Service -------------------- //

export const questionService = {
  // GET single question
  getQuestion: async (question_id: string): Promise<QuestionBundle> => {
    try {
      const res = await api.get(`${BASE}/${question_id}`);
      return res.data;
    } catch (error: any) {
      throw new Error(
        extractErrorMessage(error.response?.data, "Question not found")
      );
    }
  },

  // LIST questions
  listQuestions: async (
    params: QuestionListQuery = {}
  ): Promise<QuestionBundle[]> => {
    try {
      const res = await api.get(`${BASE}/`, {
        params: {
          subject_id: params.subject_id,
          chapter_id: params.chapter_id,
          topic_id: params.topic_id,
          limit: params.limit ?? 50,
          offset: params.offset ?? 0,
        },
      });

      return res.data;
    } catch (error: any) {
      throw new Error(
        extractErrorMessage(error.response?.data, "Failed to fetch questions")
      );
    }
  },

  // SEARCH questions
  searchQuestions: async (
    q: string,
    limit: number = 20
  ): Promise<QuestionBundle[]> => {
    try {
      const res = await api.get(`${BASE}/search/text`, {
        params: { q, limit },
      });

      return res.data;
    } catch (error: any) {
      throw new Error(
        extractErrorMessage(error.response?.data, "Search failed")
      );
    }
  },

  // UPDATE question (FLAT PAYLOAD ONLY)
  updateQuestion: async (
    question_id: string,
    payload: QuestionBundleUpdateRequest
  ): Promise<QuestionBundle> => {
    try {
      const cleanPayload: QuestionBundleUpdateRequest = {
        content: payload.content,
        explanation: payload.explanation,
        difficulty: payload.difficulty,
        importance: payload.importance,
        tags: payload.tags,
        model_answer: payload.model_answer,
        options: payload.options,
      };

      const res = await api.put(`${BASE}/${question_id}`, cleanPayload);
      return res.data;
    } catch (error: any) {
      throw new Error(
        extractErrorMessage(error.response?.data, "Failed to update question")
      );
    }
  },

  // DELETE question
  deleteQuestion: async (
    question_id: string
  ): Promise<DeleteQuestionResponse> => {
    try {
      const res = await api.delete(`${BASE}/${question_id}`);
      return res.data;
    } catch (error: any) {
      throw new Error(
        extractErrorMessage(error.response?.data, "Failed to delete question")
      );
    }
  },
};