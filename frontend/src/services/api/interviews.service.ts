import { assertApiSuccess } from "@/lib/errors";
import type { ApiResponse } from "@/types/api";
import type {
  FinishInterviewResponse,
  InterviewDetailResponse,
  InterviewHistoryResponse,
  StartInterviewRequest,
  StartInterviewResponse,
  SubmitAnswerResponse,
} from "@/types/interview";

import { apiClient } from "./client";

export const interviewsService = {
  async start(payload: StartInterviewRequest): Promise<StartInterviewResponse> {
    const { data } = await apiClient.post<ApiResponse<StartInterviewResponse>>(
      "/interviews/start",
      payload,
    );
    assertApiSuccess(data);
    return data.data;
  },

  async submitAnswer(
    sessionId: string,
    questionId: string,
    answer: string,
  ): Promise<SubmitAnswerResponse> {
    const { data } = await apiClient.post<ApiResponse<SubmitAnswerResponse>>(
      `/interviews/${sessionId}/answer`,
      { question_id: questionId, answer },
    );
    assertApiSuccess(data);
    return data.data;
  },

  async finish(sessionId: string): Promise<FinishInterviewResponse> {
    const { data } = await apiClient.post<ApiResponse<FinishInterviewResponse>>(
      `/interviews/${sessionId}/finish`,
    );
    assertApiSuccess(data);
    return data.data;
  },

  async getHistory(): Promise<InterviewHistoryResponse> {
    const { data } = await apiClient.get<ApiResponse<InterviewHistoryResponse>>(
      "/interviews/history",
    );
    assertApiSuccess(data);
    return data.data;
  },

  async getSession(sessionId: string): Promise<InterviewDetailResponse> {
    const { data } = await apiClient.get<ApiResponse<InterviewDetailResponse>>(
      `/interviews/${sessionId}`,
    );
    assertApiSuccess(data);
    return data.data;
  },
};
