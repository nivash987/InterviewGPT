"use client";

import { FormEvent, useCallback, useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";

import { ApplicationTimeline } from "@/components/jobs/application-timeline";
import { StatusBadge } from "@/components/jobs/status-badge";
import { DashboardShell } from "@/components/layout/dashboard-shell";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ROUTES } from "@/constants/routes";
import { useAuth } from "@/hooks/use-auth";
import { hasAccessToken } from "@/lib/auth/tokens";
import { jobsService } from "@/services/api/jobs.service";
import { APPLICATION_STATUSES, type ApplicationStatus, type JobApplicationDetail } from "@/types/jobs";

export default function JobApplicationDetailPage() {
  const params = useParams();
  const router = useRouter();
  const { isAuthenticated } = useAuth();
  const applicationId = params.id as string;

  const [application, setApplication] = useState<JobApplicationDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [noteTitle, setNoteTitle] = useState("");
  const [noteContent, setNoteContent] = useState("");
  const [reminderTitle, setReminderTitle] = useState("");
  const [reminderAt, setReminderAt] = useState("");

  const loadApplication = useCallback(async () => {
    if (!hasAccessToken() || !applicationId) return;
    setLoading(true);
    setError(null);
    try {
      const data = await jobsService.get(applicationId);
      setApplication(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load application");
    } finally {
      setLoading(false);
    }
  }, [applicationId]);

  useEffect(() => {
    if (!isAuthenticated) {
      router.replace(ROUTES.login);
      return;
    }
    void loadApplication();
  }, [isAuthenticated, loadApplication, router]);

  const handleStatusChange = async (status: ApplicationStatus) => {
    try {
      await jobsService.updateStatus(applicationId, { status });
      await loadApplication();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update status");
    }
  };

  const handleAddNote = async (event: FormEvent) => {
    event.preventDefault();
    if (!noteTitle.trim() || !noteContent.trim()) return;
    try {
      await jobsService.addNote(applicationId, {
        title: noteTitle.trim(),
        content: noteContent.trim(),
      });
      setNoteTitle("");
      setNoteContent("");
      await loadApplication();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to add note");
    }
  };

  const handleAddReminder = async (event: FormEvent) => {
    event.preventDefault();
    if (!reminderTitle.trim() || !reminderAt) return;
    try {
      await jobsService.addReminder(applicationId, {
        title: reminderTitle.trim(),
        remind_at: new Date(reminderAt).toISOString(),
      });
      setReminderTitle("");
      setReminderAt("");
      await loadApplication();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to add reminder");
    }
  };

  const handleDelete = async () => {
    if (!confirm("Delete this application?")) return;
    try {
      await jobsService.delete(applicationId);
      router.push(ROUTES.jobs);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete application");
    }
  };

  if (loading) {
    return (
      <DashboardShell title="Application" description="Loading…">
        <p className="text-sm text-muted-foreground">Loading application…</p>
      </DashboardShell>
    );
  }

  if (!application) {
    return (
      <DashboardShell title="Application" description="Not found">
        <p className="text-sm text-destructive">{error ?? "Application not found."}</p>
      </DashboardShell>
    );
  }

  return (
    <DashboardShell
      title={`${application.role_title} at ${application.company_name}`}
      description="Application details, timeline, and notes."
    >
      <div className="mx-auto max-w-4xl space-y-6">
        {error && (
          <p className="rounded-md border border-destructive/50 bg-destructive/10 px-4 py-2 text-sm text-destructive">
            {error}
          </p>
        )}

        <Card>
          <CardHeader>
            <div className="flex flex-wrap items-center justify-between gap-2">
              <CardTitle>{application.company_name}</CardTitle>
              <StatusBadge status={application.status} />
            </div>
            <CardDescription>{application.role_title}</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {application.location && <p className="text-sm">Location: {application.location}</p>}
            {application.salary_range && (
              <p className="text-sm">Salary: {application.salary_range}</p>
            )}
            {application.job_url && (
              <a
                href={application.job_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm text-primary hover:underline"
              >
                View job posting
              </a>
            )}
            {application.description && (
              <p className="text-sm text-muted-foreground">{application.description}</p>
            )}
            <div className="flex flex-wrap items-center gap-2">
              <Label htmlFor="status-select" className="sr-only">
                Update status
              </Label>
              <select
                id="status-select"
                className="rounded-md border bg-background px-3 py-2 text-sm"
                value={application.status}
                onChange={(e) => void handleStatusChange(e.target.value as ApplicationStatus)}
              >
                {APPLICATION_STATUSES.map((s) => (
                  <option key={s} value={s}>
                    {s.replace(/_/g, " ")}
                  </option>
                ))}
              </select>
              <Button variant="destructive" size="sm" onClick={() => void handleDelete()}>
                Delete
              </Button>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Timeline</CardTitle>
            <CardDescription>Status changes and milestones</CardDescription>
          </CardHeader>
          <CardContent>
            <ApplicationTimeline events={application.status_history} />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Interview notes</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {application.interview_notes.length === 0 ? (
              <p className="text-sm text-muted-foreground">No notes yet.</p>
            ) : (
              <ul className="space-y-3">
                {application.interview_notes.map((note) => (
                  <li key={note.id} className="rounded-md border p-3">
                    <p className="font-medium">{note.title}</p>
                    <p className="mt-1 text-sm text-muted-foreground">{note.content}</p>
                  </li>
                ))}
              </ul>
            )}
            <form onSubmit={handleAddNote} className="space-y-2 border-t pt-4">
              <Input
                placeholder="Note title"
                value={noteTitle}
                onChange={(e) => setNoteTitle(e.target.value)}
              />
              <textarea
                className="flex min-h-[60px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                placeholder="Note content"
                value={noteContent}
                onChange={(e) => setNoteContent(e.target.value)}
              />
              <Button type="submit" size="sm">
                Add note
              </Button>
            </form>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Reminders</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {application.reminders.length === 0 ? (
              <p className="text-sm text-muted-foreground">No reminders set.</p>
            ) : (
              <ul className="space-y-2">
                {application.reminders.map((reminder) => (
                  <li key={reminder.id} className="flex justify-between text-sm">
                    <span>{reminder.title}</span>
                    <span className="text-muted-foreground">
                      {new Date(reminder.remind_at).toLocaleString()}
                      {reminder.is_completed && " (done)"}
                    </span>
                  </li>
                ))}
              </ul>
            )}
            <form onSubmit={handleAddReminder} className="space-y-2 border-t pt-4">
              <Input
                placeholder="Reminder title"
                value={reminderTitle}
                onChange={(e) => setReminderTitle(e.target.value)}
              />
              <Input
                type="datetime-local"
                value={reminderAt}
                onChange={(e) => setReminderAt(e.target.value)}
              />
              <Button type="submit" size="sm">
                Add reminder
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </DashboardShell>
  );
}
