import api from "@/lib/api";

// -------------------- Types -------------------- //

export interface RunPipelineResponse {
  success: boolean;
  data: any;
}

// ---- Chunk Types ---- //
export interface CreateChunkRequest {
  book_id: string;
  subject_id: string;
  chapter_id?: string | null;
  topic_id?: string | null;
  chunk_index: number;
  content: string;
}

export interface ChunkResponse {
  id: string;
  book_id: string;
  subject_id: string;
  chapter_id?: string | null;
  topic_id?: string | null;
  chunk_index: number;
  content: string;
}

export interface ListChunksResponse {
  items: ChunkResponse[];
}

export interface UpdateChunkRequest {
  chapter_id?: string | null;
  topic_id?: string | null;
  chunk_index?: number | null;
  content?: string | null;
}

export interface DeleteChunkResponse {
  success: boolean;
}

// -------------------- Error Helper -------------------- //

const extractErrorMessage = (data: any, fallback: string): string => {
  if (Array.isArray(data?.detail)) {
    return data.detail
      .map((err: any) => {
        const field = err.loc ? err.loc[err.loc.length - 1] : "field";
        return `${field}: ${err.msg || err.message}`;
      })
      .join(", ");
  }

  return data?.detail || data?.message || fallback;
};

// -------------------- Question Service -------------------- //

export const questionService = {

  // -------------------- Run Segmentation Pipeline -------------------- //
  runSegmentationPipeline: async (
    subjectId: string,
    bookId: string
  ): Promise<RunPipelineResponse> => {
    try {
      const res = await api.post(
        `/question/run_segmentation_pipeline/${subjectId}`,
        null,
        {
          params: {
            book_id: bookId,
          },
        }
      );

      return res.data;
    } catch (error: any) {
      throw new Error(
        extractErrorMessage(
          error.response?.data,
          "Failed to run segmentation pipeline"
        )
      );
    }
  },

  // -------------------- Create Chunk -------------------- //
  createChunk: async (
    payload: CreateChunkRequest
  ): Promise<ChunkResponse> => {
    try {
      const res = await api.post("/question/chunks", payload);
      return res.data;
    } catch (error: any) {
      throw new Error(
        extractErrorMessage(
          error.response?.data,
          "Failed to create chunk"
        )
      );
    }
  },

  // -------------------- Get Chunk -------------------- //
  getChunk: async (chunkId: string): Promise<ChunkResponse> => {
    try {
      const res = await api.get(`/question/chunks/${chunkId}`);
      return res.data;
    } catch (error: any) {
      throw new Error(
        extractErrorMessage(
          error.response?.data,
          "Chunk not found"
        )
      );
    }
  },

  // -------------------- List Chunks -------------------- //
  listChunks: async (): Promise<ListChunksResponse> => {
    try {
      const res = await api.get("/question/chunks");
      return res.data;
    } catch (error: any) {
      throw new Error(
        extractErrorMessage(
          error.response?.data,
          "Failed to fetch chunks"
        )
      );
    }
  },

  // -------------------- Update Chunk -------------------- //
  updateChunk: async (
    chunkId: string,
    payload: UpdateChunkRequest
  ): Promise<ChunkResponse> => {
    try {
      const res = await api.put(
        `/question/chunks/${chunkId}`,
        payload
      );

      return res.data;

    } catch (error: any) {
      throw new Error(
        extractErrorMessage(
          error.response?.data,
          "Failed to update chunk"
        )
      );
    }
  },

  // -------------------- Delete Chunk -------------------- //
  deleteChunk: async (
    chunkId: string
  ): Promise<DeleteChunkResponse> => {
    try {
      const res = await api.delete(
        `/question/chunks/${chunkId}`
      );

      return res.data;

    } catch (error: any) {
      throw new Error(
        extractErrorMessage(
          error.response?.data,
          "Failed to delete chunk"
        )
      );
    }
  },

  // -------------------- Delete All Chunks By Subject + Book -------------------- //
  deleteAllChunksBySubjectAndBook: async (
    subjectId: string,
    bookId: string
  ): Promise<DeleteChunkResponse> => {
    try {
      const res = await api.delete(
        `/question/chunks/subject/${subjectId}/book/${bookId}`
      );

      return res.data;

    } catch (error: any) {
      throw new Error(
        extractErrorMessage(
          error.response?.data,
          "Failed to delete chunks"
        )
      );
    }
  },
};