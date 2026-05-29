"use client";

import { useRef, useState } from "react";
import { RefreshCw, Trash2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import type { Resume } from "@/types/resume";
import { cn } from "@/lib/utils";

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function formatDate(iso: string): string {
  return new Date(iso).toLocaleString(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

interface ResumeHistoryTableProps {
  resumes: Resume[];
  onDelete: (resumeId: string) => Promise<void>;
  onReplace: (resumeId: string, file: File, onProgress: (percent: number) => void) => Promise<void>;
  loading?: boolean;
}

export function ResumeHistoryTable({
  resumes,
  onDelete,
  onReplace,
  loading = false,
}: ResumeHistoryTableProps) {
  const [replacingId, setReplacingId] = useState<string | null>(null);
  const [busyId, setBusyId] = useState<string | null>(null);
  const replaceInputRef = useRef<HTMLInputElement>(null);

  const triggerReplace = (resumeId: string) => {
    setReplacingId(resumeId);
    replaceInputRef.current?.click();
  };

  const handleReplaceSelected = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    const resumeId = replacingId;
    event.target.value = "";
    setReplacingId(null);
    if (!file || !resumeId) return;

    setBusyId(resumeId);
    try {
      await onReplace(resumeId, file, () => {});
    } finally {
      setBusyId(null);
    }
  };

  const handleDelete = async (resumeId: string) => {
    if (!window.confirm("Delete this resume and all versions?")) return;
    setBusyId(resumeId);
    try {
      await onDelete(resumeId);
    } finally {
      setBusyId(null);
    }
  };

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Resume history</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">Loading resumes…</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Resume history</CardTitle>
        <CardDescription>
          {resumes.length === 0
            ? "No resumes uploaded yet."
            : `${resumes.length} resume${resumes.length === 1 ? "" : "s"} on file`}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <input
          ref={replaceInputRef}
          type="file"
          accept=".pdf,.docx"
          className="hidden"
          onChange={(e) => void handleReplaceSelected(e)}
        />

        {resumes.length === 0 ? (
          <p className="text-sm text-muted-foreground">
            Upload a resume above to see it listed here.
          </p>
        ) : (
          <div className="overflow-x-auto rounded-md border">
            <table className="w-full min-w-[640px] text-sm">
              <thead>
                <tr className="border-b bg-muted/50 text-left">
                  <th className="px-4 py-3 font-medium">Title</th>
                  <th className="px-4 py-3 font-medium">File</th>
                  <th className="px-4 py-3 font-medium">Size</th>
                  <th className="px-4 py-3 font-medium">Versions</th>
                  <th className="px-4 py-3 font-medium">Updated</th>
                  <th className="px-4 py-3 font-medium">Parsed</th>
                  <th className="px-4 py-3 font-medium text-right">Actions</th>
                </tr>
              </thead>
              <tbody>
                {resumes.map((resume) => {
                  const version = resume.current_version;
                  const parsed = version?.parsed_data;
                  const isBusy = busyId === resume.id;

                  return (
                    <tr key={resume.id} className={cn("border-b last:border-0", isBusy && "opacity-60")}>
                      <td className="px-4 py-3 font-medium">{resume.title ?? "Untitled"}</td>
                      <td className="px-4 py-3 text-muted-foreground">
                        {version?.original_filename ?? "—"}
                      </td>
                      <td className="px-4 py-3 text-muted-foreground">
                        {version ? formatBytes(version.file_size_bytes) : "—"}
                      </td>
                      <td className="px-4 py-3">{resume.version_count}</td>
                      <td className="px-4 py-3 text-muted-foreground">{formatDate(resume.updated_at)}</td>
                      <td className="px-4 py-3 text-muted-foreground">
                        {parsed?.name ?? parsed?.email ?? "—"}
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex justify-end gap-2">
                          <Button
                            variant="outline"
                            size="sm"
                            disabled={isBusy}
                            onClick={() => triggerReplace(resume.id)}
                          >
                            <RefreshCw className="mr-1 h-3.5 w-3.5" />
                            Replace
                          </Button>
                          <Button
                            variant="destructive"
                            size="sm"
                            disabled={isBusy}
                            onClick={() => void handleDelete(resume.id)}
                          >
                            <Trash2 className="mr-1 h-3.5 w-3.5" />
                            Delete
                          </Button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
