"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import type { JobsAnalyticsSummary } from "@/types/jobs";

interface JobsAnalyticsProps {
  analytics: JobsAnalyticsSummary;
}

function MetricCard({ label, value }: { label: string; value: string | number }) {
  return (
    <Card>
      <CardHeader className="pb-2">
        <CardDescription>{label}</CardDescription>
        <CardTitle className="text-2xl tabular-nums">{value}</CardTitle>
      </CardHeader>
    </Card>
  );
}

function StatusBarChart({ byStatus }: { byStatus: Record<string, number> }) {
  const entries = Object.entries(byStatus);
  if (entries.length === 0) {
    return <p className="text-sm text-muted-foreground">No applications yet.</p>;
  }
  const max = Math.max(...entries.map(([, count]) => count), 1);

  return (
    <div className="flex h-40 items-end gap-2">
      {entries.map(([status, count]) => (
        <div key={status} className="flex flex-1 flex-col items-center gap-1">
          <span className="text-xs font-medium tabular-nums">{count}</span>
          <div className="relative w-full flex-1">
            <div
              className="absolute bottom-0 w-full rounded-t bg-primary transition-all"
              style={{ height: `${Math.max(4, (count / max) * 100)}%` }}
            />
          </div>
          <span className="max-w-full truncate text-[10px] text-muted-foreground">
            {status.replace(/_/g, " ")}
          </span>
        </div>
      ))}
    </div>
  );
}

export function JobsAnalytics({ analytics }: JobsAnalyticsProps) {
  return (
    <div className="space-y-6">
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
        <MetricCard label="Total Applications" value={analytics.total_applications} />
        <MetricCard label="Interviews Scheduled" value={analytics.interviews_scheduled} />
        <MetricCard label="Offers Received" value={analytics.offers_received} />
        <MetricCard label="Rejections" value={analytics.rejections} />
        <MetricCard label="Success Rate" value={`${analytics.success_rate}%`} />
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Applications by Status</CardTitle>
          <CardDescription>Distribution across your pipeline</CardDescription>
        </CardHeader>
        <CardContent>
          <StatusBarChart byStatus={analytics.by_status} />
        </CardContent>
      </Card>
    </div>
  );
}
