import { assertApiSuccess } from "@/lib/errors";
import type { ApiResponse } from "@/types/api";
import type { Resume, ResumeHistoryResponse, ResumeListResponse } from "@/types/resume";

import { apiClient } from "./client";

export type UploadProgressCallback = (percent: number) => void;

function buildFormData(file: File, title?: string): FormData {
  const formData = new FormData();
  formData.append("file", file);
  if (title) {
    formData.append("title", title);
  }
  return formData;
}

export const resumesService = {
  async list(): Promise<ResumeListResponse> {
    const { data } = await apiClient.get<ApiResponse<ResumeListResponse>>("/resumes");
    assertApiSuccess(data);
    return data.data;
  },

  async get(resumeId: string): Promise<Resume> {
    const { data } = await apiClient.get<ApiResponse<Resume>>(`/resumes/${resumeId}`);
    assertApiSuccess(data);
    return data.data;
  },

  async getHistory(resumeId: string): Promise<ResumeHistoryResponse> {
    const { data } = await apiClient.get<ApiResponse<ResumeHistoryResponse>>(
      `/resumes/${resumeId}/history`,
    );
    assertApiSuccess(data);
    return data.data;
  },

  async upload(
    file: File,
    options?: { title?: string; onProgress?: UploadProgressCallback },
  ): Promise<Resume> {
    const formData = buildFormData(file, options?.title);
    const { data } = await apiClient.post<ApiResponse<Resume>>("/resumes/upload", formData, {
      onUploadProgress: (event) => {
        if (!options?.onProgress || !event.total) return;
        options.onProgress(Math.round((event.loaded * 100) / event.total));
      },
    });
    assertApiSuccess(data);
    return data.data;
  },

  async replace(
    resumeId: string,
    file: File,
    options?: { onProgress?: UploadProgressCallback },
  ): Promise<Resume> {
    const formData = new FormData();
    formData.append("file", file);
    const { data } = await apiClient.put<ApiResponse<Resume>>(
      `/resumes/${resumeId}/replace`,
      formData,
      {
        onUploadProgress: (event) => {
          if (!options?.onProgress || !event.total) return;
          options.onProgress(Math.round((event.loaded * 100) / event.total));
        },
      },
    );
    assertApiSuccess(data);
    return data.data;
  },

  async delete(resumeId: string): Promise<void> {
    const { data } = await apiClient.delete<ApiResponse<unknown>>(`/resumes/${resumeId}`);
    assertApiSuccess(data);
  },
};
