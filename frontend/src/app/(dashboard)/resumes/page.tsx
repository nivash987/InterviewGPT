"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { ResumeHistoryTable } from "@/components/resume/resume-history-table";
import { ResumeUploadZone } from "@/components/resume/resume-upload-zone";
import { DashboardShell } from "@/components/layout/dashboard-shell";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ROUTES } from "@/constants/routes";
import { useAuth } from "@/hooks/use-auth";
import { hasAccessToken } from "@/lib/auth/tokens";
import { resumesService } from "@/services/api/resumes.service";
import type { Resume } from "@/types/resume";

export default function ResumesPage() {
  const router = useRouter();
  const { isAuthenticated } = useAuth();
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [loading, setLoading] = useState(true);
  const [title, setTitle] = useState("");
  const [error, setError] = useState<string | null>(null);

  const loadResumes = useCallback(async () => {
    if (!hasAccessToken()) {
      setResumes([]);
      setLoading(false);
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const data = await resumesService.list();
      setResumes(data.items);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load resumes");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (!isAuthenticated) {
      router.replace(ROUTES.login);
      return;
    }
    void loadResumes();
  }, [isAuthenticated, loadResumes, router]);

  const handleUpload = async (file: File, onProgress: (percent: number) => void) => {
    await resumesService.upload(file, { title: title.trim() || undefined, onProgress });
    setTitle("");
    await loadResumes();
  };

  const handleReplace = async (
    resumeId: string,
    file: File,
    onProgress: (percent: number) => void,
  ) => {
    await resumesService.replace(resumeId, file, { onProgress });
    await loadResumes();
  };

  const handleDelete = async (resumeId: string) => {
    await resumesService.delete(resumeId);
    await loadResumes();
  };

  return (
    <DashboardShell
      title="Resumes"
      description="Upload, manage, and parse your resumes."
    >
      <div className="mx-auto max-w-5xl space-y-6">
        {error && (
          <p className="rounded-md border border-destructive/50 bg-destructive/10 px-4 py-2 text-sm text-destructive">
            {error}
          </p>
        )}

        <Card>
          <CardHeader>
            <CardTitle>Upload resume</CardTitle>
            <CardDescription>
              PDF or DOCX files are parsed automatically for contact info, skills, experience, and more.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2 max-w-md">
              <Label htmlFor="resume-title">Title (optional)</Label>
              <Input
                id="resume-title"
                placeholder="e.g. Software Engineer Resume"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
              />
            </div>
            <ResumeUploadZone onUpload={handleUpload} />
          </CardContent>
        </Card>

        <ResumeHistoryTable
          resumes={resumes}
          loading={loading}
          onDelete={handleDelete}
          onReplace={handleReplace}
        />
      </div>
    </DashboardShell>
  );
}
