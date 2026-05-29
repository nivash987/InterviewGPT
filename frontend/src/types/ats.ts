export interface SectionScores {
  contact_information: number;
  summary: number;
  skills: number;
  experience: number;
  education: number;
  projects: number;
}

export interface KeywordCoverage {
  matched_keywords: number;
  total_keywords: number;
  coverage_percent: number;
}

export interface RecommendedRole {
  role_name: string;
  match_score: number;
  matched_required: string[];
  matched_preferred: string[];
  missing_required: string[];
}

export interface AtsAnalysisResult {
  ats_score: number;
  completeness_score: number;
  section_scores: SectionScores;
  skills_found: string[];
  missing_skills: string[];
  keyword_coverage: KeywordCoverage;
  strengths: string[];
  weaknesses: string[];
  suggestions: string[];
  recommended_roles: RecommendedRole[];
}

export interface AtsAnalysisPublic extends AtsAnalysisResult {
  id: string;
  resume_id: string;
  created_at: string;
}

export interface AtsHistoryItem {
  id: string;
  resume_id: string;
  resume_title: string | null;
  ats_score: number;
  completeness_score: number;
  created_at: string;
}

export interface AtsHistoryResponse {
  items: AtsHistoryItem[];
  total: number;
}

export const SECTION_LABELS: Record<keyof SectionScores, string> = {
  contact_information: "Contact Information",
  summary: "Summary",
  skills: "Skills",
  experience: "Experience",
  education: "Education",
  projects: "Projects",
};
