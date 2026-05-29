"use client";

import { Loader2, Search } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import type { Resume } from "@/types/resume";

interface ResumeSelectorProps {
  resumes: Resume[];
  selectedId: string | null;
  onSelect: (id: string) => void;
  onAnalyze: () => void;
  analyzing: boolean;
  loading: boolean;
}

export function ResumeSelector({
  resumes,
  selectedId,
  onSelect,
  onAnalyze,
  analyzing,
  loading,
}: ResumeSelectorProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Select resume</CardTitle>
        <CardDescription>
          Choose an uploaded resume and run a rule-based ATS analysis.
        </CardDescription>
      </CardHeader>
      <CardContent className="flex flex-col gap-4 sm:flex-row sm:items-end">
        <div className="flex-1 space-y-2">
          <label htmlFor="resume-select" className="text-sm font-medium">
            Resume
          </label>
          <select
            id="resume-select"
            value={selectedId ?? ""}
            onChange={(e) => onSelect(e.target.value)}
            disabled={loading || resumes.length === 0}
            className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
          >
            <option value="" disabled>
              {loading ? "Loading resumes…" : resumes.length === 0 ? "No resumes uploaded" : "Select a resume"}
            </option>
            {resumes.map((resume) => (
              <option key={resume.id} value={resume.id}>
                {resume.title ?? resume.current_version?.original_filename ?? resume.id}
              </option>
            ))}
          </select>
        </div>
        <Button
          onClick={onAnalyze}
          disabled={!selectedId || analyzing}
          className="gap-2 sm:w-auto w-full"
        >
          {analyzing ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              Analyzing…
            </>
          ) : (
            <>
              <Search className="h-4 w-4" />
              Analyze
            </>
          )}
        </Button>
      </CardContent>
    </Card>
  );
}
