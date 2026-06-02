import { assertApiSuccess } from "@/lib/errors";
import type { ApiResponse } from "@/types/api";
import type {
  CareerCoachDashboard,
  CareerRoadmap,
  LearningRecommendation,
  ReadinessScore,
  SkillGapAnalysis,
  UserGoal,
  UserGoalCreatePayload,
  UserSkill,
  ProgressUpdatePayload,
  WeaknessItem,
} from "@/types/career-coach";

import { apiClient } from "./client";

export const careerCoachService = {
  async getDashboard(): Promise<CareerCoachDashboard> {
    const { data } = await apiClient.get<ApiResponse<CareerCoachDashboard>>("/career-coach/dashboard");
    assertApiSuccess(data);
    return data.data;
  },

  async setGoal(payload: UserGoalCreatePayload): Promise<UserGoal> {
    const { data } = await apiClient.post<ApiResponse<UserGoal>>("/career-coach/goals", payload);
    assertApiSuccess(data);
    return data.data;
  },

  async getGoal(): Promise<UserGoal | null> {
    const { data } = await apiClient.get<ApiResponse<UserGoal | null>>("/career-coach/goals");
    assertApiSuccess(data);
    return data.data;
  },

  async listSkills(): Promise<UserSkill[]> {
    const { data } = await apiClient.get<ApiResponse<UserSkill[]>>("/career-coach/skills");
    assertApiSuccess(data);
    return data.data;
  },

  async syncSkillsFromAts(): Promise<UserSkill[]> {
    const { data } = await apiClient.post<ApiResponse<UserSkill[]>>("/career-coach/skills/sync-ats");
    assertApiSuccess(data);
    return data.data;
  },

  async generateRoadmap(): Promise<CareerRoadmap> {
    const { data } = await apiClient.post<ApiResponse<CareerRoadmap>>("/career-coach/roadmap/generate");
    assertApiSuccess(data);
    return data.data;
  },

  async getRoadmap(): Promise<CareerRoadmap> {
    const { data } = await apiClient.get<ApiResponse<CareerRoadmap>>("/career-coach/roadmap");
    assertApiSuccess(data);
    return data.data;
  },

  async getSkillGaps(): Promise<SkillGapAnalysis> {
    const { data } = await apiClient.get<ApiResponse<SkillGapAnalysis>>("/career-coach/skill-gaps");
    assertApiSuccess(data);
    return data.data;
  },

  async computeReadiness(): Promise<ReadinessScore> {
    const { data } = await apiClient.post<ApiResponse<ReadinessScore>>("/career-coach/readiness/compute");
    assertApiSuccess(data);
    return data.data;
  },

  async getReadiness(): Promise<ReadinessScore> {
    const { data } = await apiClient.get<ApiResponse<ReadinessScore>>("/career-coach/readiness");
    assertApiSuccess(data);
    return data.data;
  },

  async updateProgress(milestoneId: string, payload: ProgressUpdatePayload) {
    const { data } = await apiClient.patch<ApiResponse<unknown>>(
      `/career-coach/progress/${milestoneId}`,
      payload,
    );
    assertApiSuccess(data);
    return data.data;
  },

  async getRecommendations(): Promise<LearningRecommendation[]> {
    const { data } = await apiClient.get<ApiResponse<LearningRecommendation[]>>(
      "/career-coach/recommendations",
    );
    assertApiSuccess(data);
    return data.data;
  },

  async getWeaknesses(): Promise<WeaknessItem[]> {
    const { data } = await apiClient.get<ApiResponse<WeaknessItem[]>>("/career-coach/weaknesses");
    assertApiSuccess(data);
    return data.data;
  },
};
