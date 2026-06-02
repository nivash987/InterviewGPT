export const APPLICATION_STATUSES = [
  "applied",
  "screening",
  "interview_scheduled",
  "interview_completed",
  "offer",
  "rejected",
  "withdrawn",
] as const;

export type ApplicationStatus = (typeof APPLICATION_STATUSES)[number];

export interface JobApplication {
  id: string;
  company_name: string;
  role_title: string;
  status: ApplicationStatus;
  location: string | null;
  job_url: string | null;
  salary_range: string | null;
  description: string | null;
  applied_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface StatusHistoryEvent {
  id: string;
  from_status: string | null;
  to_status: string;
  note: string | null;
  created_at: string;
}

export interface InterviewNote {
  id: string;
  application_id: string;
  title: string;
  content: string;
  created_at: string;
  updated_at: string;
}

export interface Reminder {
  id: string;
  application_id: string;
  title: string;
  remind_at: string;
  is_completed: boolean;
  created_at: string;
}

export interface JobApplicationDetail extends JobApplication {
  status_history: StatusHistoryEvent[];
  interview_notes: InterviewNote[];
  reminders: Reminder[];
}

export interface JobApplicationListResponse {
  items: JobApplication[];
}

export interface JobsAnalyticsSummary {
  total_applications: number;
  interviews_scheduled: number;
  offers_received: number;
  rejections: number;
  success_rate: number;
  by_status: Record<string, number>;
}

export interface TimelineResponse {
  application_id: string;
  events: StatusHistoryEvent[];
}

export interface JobApplicationCreatePayload {
  company_name: string;
  role_title: string;
  status?: ApplicationStatus;
  location?: string;
  job_url?: string;
  salary_range?: string;
  description?: string;
  applied_at?: string;
}

export interface StatusUpdatePayload {
  status: ApplicationStatus;
  note?: string;
}
