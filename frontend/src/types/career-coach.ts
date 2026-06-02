export interface UserGoal {
  id: string;
  target_role: string;
  target_timeline_months: number | null;
  description: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface UserSkill {
  id: string;
  skill_name: string;
  proficiency_level: string;
  source: string;
  created_at: string;
  updated_at: string;
}

export interface RoadmapMilestone {
  id: string;
  title: string;
  description: string;
  order: number;
  estimated_weeks: number;
  skills: string[];
  status: string;
}

export interface CareerRoadmap {
  id: string;
  goal_id: string | null;
  title: string;
  target_role: string;
  milestones: RoadmapMilestone[];
  status: string;
  progress_percent: number;
  created_at: string;
  updated_at: string;
}

export interface SkillGapItem {
  skill_name: string;
  priority: string;
  reason: string;
}

export interface SkillGapAnalysis {
  target_role: string;
  required_skills: string[];
  user_skills: string[];
  missing_skills: SkillGapItem[];
  coverage_percent: number;
}

export interface LearningRecommendation {
  title: string;
  description: string;
  skill: string;
  resource_type: string;
  priority: string;
}

export interface WeaknessItem {
  area: string;
  severity: string;
  description: string;
  suggested_action: string;
}

export interface ReadinessScore {
  id: string;
  overall_score: number;
  category_scores: Record<string, number>;
  weak_areas: WeaknessItem[];
  missing_skills: string[];
  recommendations: LearningRecommendation[];
  computed_at: string;
}

export interface CareerCoachDashboard {
  readiness_score: number | null;
  readiness_trend: string | null;
  missing_skills: string[];
  roadmap_progress_percent: number | null;
  weak_areas: WeaknessItem[];
  recommendations: LearningRecommendation[];
  active_goal: UserGoal | null;
  skill_coverage_percent: number | null;
}

export interface UserGoalCreatePayload {
  target_role: string;
  target_timeline_months?: number | null;
  description?: string | null;
}

export interface ProgressUpdatePayload {
  status: string;
  notes?: string | null;
}
