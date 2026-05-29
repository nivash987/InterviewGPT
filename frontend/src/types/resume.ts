export interface ParsedProject {
  title: string | null;
  description: string | null;
}

export interface ParsedExperience {
  title: string | null;
  description: string | null;
}

export interface ParsedEducation {
  title: string | null;
  description: string | null;
}

export interface ParsedResumeData {
  name: string | null;
  email: string | null;
  phone: string | null;
  skills: string[];
  projects: ParsedProject[];
  experience: ParsedExperience[];
  education: ParsedEducation[];
}

export interface ResumeVersion {
  id: string;
  resume_id: string;
  version_number: number;
  original_filename: string;
  mime_type: string;
  file_size_bytes: number;
  parsed_data: ParsedResumeData | null;
  created_at: string;
}

export interface Resume {
  id: string;
  title: string | null;
  current_version: ResumeVersion | null;
  version_count: number;
  created_at: string;
  updated_at: string;
}

export interface ResumeListResponse {
  items: Resume[];
  total: number;
}

export interface ResumeHistoryResponse {
  resume_id: string;
  versions: ResumeVersion[];
}
