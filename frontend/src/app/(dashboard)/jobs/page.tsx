"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Plus } from "lucide-react";

import { JobsAnalytics } from "@/components/jobs/jobs-analytics";
import { KanbanBoard } from "@/components/jobs/kanban-board";
import { DashboardShell } from "@/components/layout/dashboard-shell";
import { Button } from "@/components/ui/button";
import { ROUTES } from "@/constants/routes";
import { useAuth } from "@/hooks/use-auth";
import { hasAccessToken } from "@/lib/auth/tokens";
import { jobsService } from "@/services/api/jobs.service";
import type { ApplicationStatus, JobApplication, JobsAnalyticsSummary } from "@/types/jobs";

export default function JobsPage() {
  const router = useRouter();
  const { isAuthenticated } = useAuth();
  const [applications, setApplications] = useState<JobApplication[]>([]);
  const [analytics, setAnalytics] = useState<JobsAnalyticsSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = useCallback(async () => {
    if (!hasAccessToken()) {
      setApplications([]);
      setAnalytics(null);
      setLoading(false);
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const [list, summary] = await Promise.all([jobsService.list(), jobsService.getAnalytics()]);
      setApplications(list.items);
      setAnalytics(summary);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load job applications");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (!isAuthenticated) {
      router.replace(ROUTES.login);
      return;
    }
    void loadData();
  }, [isAuthenticated, loadData, router]);

  const handleStatusChange = async (applicationId: string, status: ApplicationStatus) => {
    try {
      await jobsService.updateStatus(applicationId, { status });
      await loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update status");
    }
  };

  return (
    <DashboardShell
      title="Job Applications"
      description="Track applications, interviews, and offers in one place."
    >
      <div className="mx-auto max-w-7xl space-y-6">
        <div className="flex justify-end">
          <Button asChild>
            <Link href={`${ROUTES.jobs}/new`}>
              <Plus className="mr-2 h-4 w-4" />
              New Application
            </Link>
          </Button>
        </div>

        {error && (
          <p className="rounded-md border border-destructive/50 bg-destructive/10 px-4 py-2 text-sm text-destructive">
            {error}
          </p>
        )}

        {loading ? (
          <p className="text-sm text-muted-foreground">Loading applications…</p>
        ) : (
          <>
            {analytics && <JobsAnalytics analytics={analytics} />}
            <KanbanBoard applications={applications} onStatusChange={handleStatusChange} />
          </>
        )}
      </div>
    </DashboardShell>
  );
}
