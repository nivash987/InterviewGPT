"use client";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import type { DifficultyLevel, QuestionCountOption } from "@/types/interview";
import type { Resume } from "@/types/resume";

const DIFFICULTIES: { value: DifficultyLevel; label: string }[] = [
  { value: "easy", label: "Easy" },
  { value: "medium", label: "Medium" },
  { value: "hard", label: "Hard" },
];

const QUESTION_COUNTS: QuestionCountOption[] = [5, 10, 15, 20];

const DEFAULT_ROLES = [
  "Backend Developer",
  "Frontend Developer",
  "Full Stack Developer",
  "Data Engineer",
  "DevOps Engineer",
  "Software Engineer",
];

interface InterviewSetupProps {
  resumes: Resume[];
  selectedResumeId: string | null;
  onResumeChange: (id: string) => void;
  role: string;
  onRoleChange: (role: string) => void;
  difficulty: DifficultyLevel;
  onDifficultyChange: (d: DifficultyLevel) => void;
  questionCount: QuestionCountOption;
  onQuestionCountChange: (c: QuestionCountOption) => void;
  onStart: () => void;
  starting?: boolean;
  loadingResumes?: boolean;
}

export function InterviewSetup({
  resumes,
  selectedResumeId,
  onResumeChange,
  role,
  onRoleChange,
  difficulty,
  onDifficultyChange,
  questionCount,
  onQuestionCountChange,
  onStart,
  starting = false,
  loadingResumes = false,
}: InterviewSetupProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Interview setup</CardTitle>
        <CardDescription>
          Questions are generated from your resume skills, ATS analysis, and target role.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="space-y-2">
          <Label htmlFor="resume-select">Resume</Label>
          <select
            id="resume-select"
            className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
            value={selectedResumeId ?? ""}
            onChange={(e) => onResumeChange(e.target.value)}
            disabled={loadingResumes || resumes.length === 0}
          >
            {resumes.length === 0 ? (
              <option value="">No resumes uploaded</option>
            ) : (
              resumes.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.title ?? "Untitled resume"}
                </option>
              ))
            )}
          </select>
        </div>

        <div className="space-y-2">
          <Label htmlFor="role-input">Target role</Label>
          <Input
            id="role-input"
            list="role-suggestions"
            value={role}
            onChange={(e) => onRoleChange(e.target.value)}
            placeholder="e.g. Backend Developer"
          />
          <datalist id="role-suggestions">
            {DEFAULT_ROLES.map((r) => (
              <option key={r} value={r} />
            ))}
          </datalist>
        </div>

        <div className="space-y-2">
          <Label>Difficulty</Label>
          <div className="flex flex-wrap gap-2">
            {DIFFICULTIES.map((d) => (
              <Button
                key={d.value}
                type="button"
                variant={difficulty === d.value ? "default" : "outline"}
                size="sm"
                onClick={() => onDifficultyChange(d.value)}
              >
                {d.label}
              </Button>
            ))}
          </div>
        </div>

        <div className="space-y-2">
          <Label>Number of questions</Label>
          <div className="flex flex-wrap gap-2">
            {QUESTION_COUNTS.map((count) => (
              <Button
                key={count}
                type="button"
                variant={questionCount === count ? "default" : "outline"}
                size="sm"
                onClick={() => onQuestionCountChange(count)}
              >
                {count}
              </Button>
            ))}
          </div>
        </div>

        <Button
          className="w-full sm:w-auto"
          onClick={onStart}
          disabled={starting || !selectedResumeId || !role.trim() || resumes.length === 0}
        >
          {starting ? "Starting interview..." : "Start mock interview"}
        </Button>
      </CardContent>
    </Card>
  );
}
