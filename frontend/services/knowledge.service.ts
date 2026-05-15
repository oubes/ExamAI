import api from "@/lib/api";

// ---- Types ----
interface RunKnowledgePipelineResponse {
  status: string;
  file_id: string;
  subject_id: string;
  data: {
    file_id: string;
    subject_id: string;
    chunks_created: number;
    total_chunks: number;
  };
}

interface KnowledgeChunk {
  id: string;
  subject_id: string;
  document_id: string;
  chunk_index: number;
  content: string;
  summary?: string | null;
  keywords?: string[] | null;
  source_type?: string | null;
  quality_score?: number | null;
  importance_score?: number | null;
}

interface GetChunkResponse {
  status: string;
  data: KnowledgeChunk;
}

interface ListChunksResponse {
  status: string;
  count: number;
  data: KnowledgeChunk[];
}

interface DeleteChunkResponse {
  status: string;
  deleted: boolean;
}

interface UpdateChunksResponse {
  status: string;
  updated: number;
}

// ---- Helpers ----
const extractErrorMessage = (data: any, fallback: string): string => {
  if (Array.isArray(data?.detail)) {
    return data.detail
      .map((err: any) => {
        const field = err.loc ? err.loc[err.loc.length - 1] : "field";
        return `${field}: ${err.msg || err.message}`;
      })
      .join(", ");
  }

  return (
    data?.detail?.message ||
    (typeof data?.detail === "string" ? data.detail : null) ||
    data?.message ||
    fallback
  );
};

// ---- Knowledge Service ----
export const knowledgeService = {
  // ---- Run Knowledge Pipeline ----
  runKnowledgePipeline: async (
    fileId: string,
    subjectId: string
  ): Promise<RunKnowledgePipelineResponse> => {
    try {
      const res = await api.post(
        `/knowledge/pipeline/run/${fileId}`,
        null,
        {
          params: { subject_id: subjectId },
        }
      );

      return res.data;
    } catch (error: any) {
      throw new Error(
        extractErrorMessage(error.response?.data, "Failed to run pipeline")
      );
    }
  },

  // ---- Get Chunk ----
  getChunk: async (chunkId: string): Promise<GetChunkResponse> => {
    try {
      const res = await api.get(`/knowledge/chunks/${chunkId}`);
      return res.data;
    } catch (error: any) {
      throw new Error(
        extractErrorMessage(error.response?.data, "Failed to fetch chunk")
      );
    }
  },

  // ---- List Subject Chunks ----
  listSubjectChunks: async (
    subjectId: string,
    limit: number = 50,
    offset: number = 0
  ): Promise<ListChunksResponse> => {
    try {
      const res = await api.get(
        `/knowledge/chunks/subject/${subjectId}`,
        {
          params: { limit, offset },
        }
      );

      return res.data;
    } catch (error: any) {
      throw new Error(
        extractErrorMessage(error.response?.data, "Failed to fetch chunks")
      );
    }
  },

  // ---- List Document Chunks ----
  listDocumentChunks: async (
    documentId: string,
    subjectId: string,
    limit: number = 100
  ): Promise<ListChunksResponse> => {
    try {
      const res = await api.get(
        `/knowledge/chunks/document/${documentId}`,
        {
          params: {
            subject_id: subjectId,
            limit,
          },
        }
      );

      return res.data;
    } catch (error: any) {
      throw new Error(
        extractErrorMessage(error.response?.data, "Failed to fetch document chunks")
      );
    }
  },

  // ---- Search Chunks ----
  searchChunks: async (
    query: string,
    limit: number = 20
  ): Promise<ListChunksResponse> => {
    try {
      const res = await api.get(`/knowledge/chunks/search`, {
        params: { query, limit },
      });

      return res.data;
    } catch (error: any) {
      throw new Error(
        extractErrorMessage(error.response?.data, "Failed to search chunks")
      );
    }
  },

  // ---- Delete Chunk ----
  deleteChunk: async (chunkId: string): Promise<DeleteChunkResponse> => {
    try {
      const res = await api.delete(`/knowledge/chunks/${chunkId}`);
      return res.data;
    } catch (error: any) {
      throw new Error(
        extractErrorMessage(error.response?.data, "Failed to delete chunk")
      );
    }
  },

  // ---- Update Chunk (FINAL MATCHED) ---- #
  updateChunk: async (
    chunkId: string,
    content: string
  ): Promise<UpdateChunksResponse> => {
    try {
      const res = await api.patch(
        `/knowledge/chunks/${chunkId}`,
        { content }
      );

      return res.data;
    } catch (error: any) {
      throw new Error(
        extractErrorMessage(error.response?.data, "Failed to update chunk")
      );
    }
  },
};