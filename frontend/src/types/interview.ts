export type DifficultyLevel = "easy" | "medium" | "hard";
export type QuestionCountOption = 5 | 10 | 15 | 20;
export type SessionStatus = "in_progress" | "completed";

export interface InterviewAnswer {
  id: string;
  question_id: string;
  answer: string;
  score: number;
  feedback: string;
}

export interface InterviewQuestion {
  id: string;
  question: string;
  category: string;
  difficulty: string;
  expected_keywords: string[];
  sort_order: number;
  answer: InterviewAnswer | null;
}

export interface InterviewSession {
  id: string;
  resume_id: string;
  role: string;
  difficulty: DifficultyLevel;
  question_count: number;
  total_score: number | null;
  status: SessionStatus;
  started_at: string;
  completed_at: string | null;
  questions: InterviewQuestion[];
}

export interface StartInterviewRequest {
  resume_id: string;
  role: string;
  difficulty: DifficultyLevel;
  question_count: QuestionCountOption;
}

export interface StartInterviewResponse {
  session: InterviewSession;
  current_question_index: number;
}

export interface SessionProgress {
  answered_count: number;
  total_questions: number;
  is_complete: boolean;
}

export interface SubmitAnswerResponse {
  answer: InterviewAnswer;
  session_progress: SessionProgress;
}

export interface CategoryScore {
  category: string;
  average_score: number;
  question_count: number;
}

export interface InterviewSummary {
  total_score: number;
  questions_answered: number;
  total_questions: number;
  average_per_category: Record<string, number>;
  strengths: string[];
  improvements: string[];
  category_breakdown: CategoryScore[];
}

export interface FinishInterviewResponse {
  session: InterviewSession;
  summary: InterviewSummary;
}

export interface InterviewHistoryItem {
  id: string;
  resume_id: string;
  resume_title: string | null;
  role: string;
  difficulty: DifficultyLevel;
  question_count: number;
  total_score: number | null;
  status: SessionStatus;
  started_at: string;
  completed_at: string | null;
}

export interface InterviewHistoryResponse {
  items: InterviewHistoryItem[];
  total: number;
}

export interface ScoreTrendPoint {
  session_id: string;
  role: string;
  total_score: number;
  completed_at: string | null;
}

export interface TopicInsight {
  category: string;
  average_score: number;
  question_count: number;
}

export interface InterviewAnalytics {
  score_trend: ScoreTrendPoint[];
  weak_topics: TopicInsight[];
  strong_topics: TopicInsight[];
}

export interface InterviewDetailResponse {
  session: InterviewSession;
  summary: InterviewSummary | null;
  analytics: InterviewAnalytics | null;
}

export type InterviewPhase = "setup" | "active" | "results" | "history";
