import { assertApiSuccess } from "@/lib/errors";
import type { ApiResponse } from "@/types/api";
import type { AtsAnalysisPublic, AtsAnalysisResult, AtsHistoryResponse } from "@/types/ats";

import { apiClient } from "./client";

export const atsService = {
  async analyze(resumeId: string): Promise<AtsAnalysisResult> {
    const { data } = await apiClient.post<ApiResponse<AtsAnalysisResult>>(
      `/ats/analyze/${resumeId}`,
    );
    assertApiSuccess(data);
    return data.data;
  },

  async getLatest(resumeId: string): Promise<AtsAnalysisPublic> {
    const { data } = await apiClient.get<ApiResponse<AtsAnalysisPublic>>(`/ats/${resumeId}`);
    assertApiSuccess(data);
    return data.data;
  },

  async getHistory(): Promise<AtsHistoryResponse> {
    const { data } = await apiClient.get<ApiResponse<AtsHistoryResponse>>("/ats/history");
    assertApiSuccess(data);
    return data.data;
  },
};
