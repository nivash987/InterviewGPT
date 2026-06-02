import { assertApiSuccess } from "@/lib/errors";
import type { ApiResponse } from "@/types/api";
import type {
  InterviewNote,
  JobApplication,
  JobApplicationCreatePayload,
  JobApplicationDetail,
  JobApplicationListResponse,
  JobsAnalyticsSummary,
  Reminder,
  StatusUpdatePayload,
  TimelineResponse,
} from "@/types/jobs";

import { apiClient } from "./client";

export const jobsService = {
  async list(): Promise<JobApplicationListResponse> {
    const { data } = await apiClient.get<ApiResponse<JobApplicationListResponse>>("/jobs");
    assertApiSuccess(data);
    return data.data;
  },

  async get(applicationId: string): Promise<JobApplicationDetail> {
    const { data } = await apiClient.get<ApiResponse<JobApplicationDetail>>(`/jobs/${applicationId}`);
    assertApiSuccess(data);
    return data.data;
  },

  async create(payload: JobApplicationCreatePayload): Promise<JobApplication> {
    const { data } = await apiClient.post<ApiResponse<JobApplication>>("/jobs", payload);
    assertApiSuccess(data);
    return data.data;
  },

  async update(
    applicationId: string,
    payload: Partial<JobApplicationCreatePayload>,
  ): Promise<JobApplication> {
    const { data } = await apiClient.patch<ApiResponse<JobApplication>>(
      `/jobs/${applicationId}`,
      payload,
    );
    assertApiSuccess(data);
    return data.data;
  },

  async delete(applicationId: string): Promise<void> {
    const { data } = await apiClient.delete<ApiResponse<unknown>>(`/jobs/${applicationId}`);
    assertApiSuccess(data);
  },

  async updateStatus(applicationId: string, payload: StatusUpdatePayload): Promise<JobApplication> {
    const { data } = await apiClient.post<ApiResponse<JobApplication>>(
      `/jobs/${applicationId}/status`,
      payload,
    );
    assertApiSuccess(data);
    return data.data;
  },

  async getTimeline(applicationId: string): Promise<TimelineResponse> {
    const { data } = await apiClient.get<ApiResponse<TimelineResponse>>(
      `/jobs/${applicationId}/timeline`,
    );
    assertApiSuccess(data);
    return data.data;
  },

  async getAnalytics(): Promise<JobsAnalyticsSummary> {
    const { data } = await apiClient.get<ApiResponse<JobsAnalyticsSummary>>(
      "/jobs/analytics/summary",
    );
    assertApiSuccess(data);
    return data.data;
  },

  async addNote(
    applicationId: string,
    payload: { title: string; content: string },
  ): Promise<InterviewNote> {
    const { data } = await apiClient.post<ApiResponse<InterviewNote>>(
      `/jobs/${applicationId}/notes`,
      payload,
    );
    assertApiSuccess(data);
    return data.data;
  },

  async addReminder(
    applicationId: string,
    payload: { title: string; remind_at: string },
  ): Promise<Reminder> {
    const { data } = await apiClient.post<ApiResponse<Reminder>>(
      `/jobs/${applicationId}/reminders`,
      payload,
    );
    assertApiSuccess(data);
    return data.data;
  },
};
