import api from "@/lib/api";

// ---- Types ----
interface SubjectPayload {
  title: string;
  code: string;
  description: string;
  is_active: boolean;
}

interface SubjectResponse {
  id: string;
  title: string;
  code: string;
  description: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

interface ListSubjectsResponse {
  items: SubjectResponse[];
}

interface DeleteResponse {
  success: boolean;
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


// ---- Education Service ----
export const educationService = {

  // ---- List Subjects ----
  listSubjects: async (): Promise<ListSubjectsResponse> => {

    try {
      const res = await api.get("/education/subjects");

      return res.data;

    } catch (error: any) {
      const data = error.response?.data;

      throw new Error(
        extractErrorMessage(
          data,
          "Failed to fetch subjects"
        )
      );
    }
  },


  // ---- List Deleted Subjects ----
  listDeletedSubjects: async (): Promise<ListSubjectsResponse> => {

    try {
      const res = await api.get(
        "/education/subjects/deleted/list"
      );

      return res.data;

    } catch (error: any) {
      const data = error.response?.data;

      throw new Error(
        extractErrorMessage(
          data,
          "Failed to fetch deleted subjects"
        )
      );
    }
  },


  // ---- Add Subject ----
  addSubject: async (
    payload: SubjectPayload
  ): Promise<SubjectResponse> => {

    try {
      const res = await api.post(
        "/education/subjects",
        payload,
      );

      return res.data;

    } catch (error: any) {
      const data = error.response?.data;

      throw new Error(
        extractErrorMessage(
          data,
          "Failed to add subject"
        )
      );
    }
  },


  // ---- Get Subject ----
  getSubject: async (
    subjectId: string
  ): Promise<SubjectResponse> => {

    try {
      const res = await api.get(
        `/education/subjects/${subjectId}`
      );

      return res.data;

    } catch (error: any) {
      const data = error.response?.data;

      throw new Error(
        extractErrorMessage(
          data,
          "Failed to fetch subject"
        )
      );
    }
  },


  // ---- Update Subject ----
  updateSubject: async (
    subjectId: string,
    payload: Partial<SubjectPayload>
  ): Promise<SubjectResponse> => {

    try {
      const res = await api.put(
        `/education/subjects/${subjectId}`,
        payload,
      );

      return res.data;

    } catch (error: any) {
      const data = error.response?.data;

      throw new Error(
        extractErrorMessage(
          data,
          "Failed to update subject"
        )
      );
    }
  },


  // ---- Delete Subject ----
  deleteSubject: async (
    subjectId: string
  ): Promise<DeleteResponse> => {

    try {
      const res = await api.delete(
        `/education/subjects/${subjectId}`
      );

      return res.data;

    } catch (error: any) {
      const data = error.response?.data;

      throw new Error(
        extractErrorMessage(
          data,
          "Failed to delete subject"
        )
      );
    }
  },


  // ---- Hard Delete Subject ----
  hardDeleteSubject: async (
    subjectId: string
  ): Promise<DeleteResponse> => {

    try {
      const res = await api.delete(
        `/education/subjects/${subjectId}/hard`
      );

      return res.data;

    } catch (error: any) {
      const data = error.response?.data;

      throw new Error(
        extractErrorMessage(
          data,
          "Failed to hard delete subject"
        )
      );
    }
  },


  // ---- Restore Subject ----
  restoreSubject: async (
    subjectId: string
  ): Promise<SubjectResponse> => {

    try {
      const res = await api.post(
        `/education/subjects/${subjectId}/restore`
      );

      return res.data;

    } catch (error: any) {
      const data = error.response?.data;

      throw new Error(
        extractErrorMessage(
          data,
          "Failed to restore subject"
        )
      );
    }
  },
};