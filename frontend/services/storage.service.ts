import api from "@/lib/api";

// ---- Types ----
export interface StorageFile {
  id: string;
  user_id: string;

  category: string;

  original_name: string;
  stored_name: string;

  path: string;
  content_type: string;

  size: number;

  processing_status: string;
  processing_error?: string | null;

  is_processed: boolean;

  created_at: string;
}

export interface UploadStats {
  total: number;
  processed: number;
  failed: number;
}

export interface DeleteResponse {
  deleted: boolean;
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

  return data?.detail || data?.message || fallback;
};

// ---- Storage Service ----
export const storageService = {
  // ---- List User Uploads ----
  listFiles: async (
    params: {
      category?: string;
      limit?: number;
      offset?: number;
    } = {}
  ): Promise<StorageFile[]> => {
    try {
      const res = await api.get("/upload/", {
        params: {
          category: params.category,
          limit: params.limit ?? 50,
          offset: params.offset ?? 0,
        },
      });

      return res.data;
    } catch (error: any) {
      throw new Error(
        extractErrorMessage(
          error.response?.data,
          "Failed to fetch files"
        )
      );
    }
  },

  // ---- Upload File ----
  uploadFile: async (
    file: File,
    category: string
  ): Promise<StorageFile> => {
    try {
      const formData = new FormData();

      formData.append("file", file);

      const res = await api.post(
        `/upload/${category}`,
        formData
      );

      return res.data;
    } catch (error: any) {
      throw new Error(
        extractErrorMessage(
          error.response?.data,
          "Upload failed"
        )
      );
    }
  },

  // ---- Get Single Upload ----
  getFile: async (
    fileId: string
  ): Promise<StorageFile> => {
    try {
      const res = await api.get(`/upload/${fileId}`);

      return res.data;
    } catch (error: any) {
      throw new Error(
        extractErrorMessage(
          error.response?.data,
          "File not found"
        )
      );
    }
  },

  // ---- Delete Upload ----
  deleteFile: async (
    fileId: string
  ): Promise<DeleteResponse> => {
    try {
      const res = await api.delete(`/upload/${fileId}`);

      return res.data;
    } catch (error: any) {
      throw new Error(
        extractErrorMessage(
          error.response?.data,
          "Failed to delete file"
        )
      );
    }
  },

  // ---- Upload Stats ----
  getStats: async (): Promise<UploadStats> => {
    try {
      const res = await api.get("/upload/stats/me");

      return res.data;
    } catch (error: any) {
      throw new Error(
        extractErrorMessage(
          error.response?.data,
          "Failed to fetch stats"
        )
      );
    }
  },
};