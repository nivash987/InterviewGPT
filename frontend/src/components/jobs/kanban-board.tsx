"use client";

import Link from "next/link";

import { StatusBadge } from "@/components/jobs/status-badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ROUTES } from "@/constants/routes";
import type { ApplicationStatus, JobApplication } from "@/types/jobs";

const KANBAN_COLUMNS: { status: ApplicationStatus; label: string }[] = [
  { status: "applied", label: "Applied" },
  { status: "screening", label: "Screening" },
  { status: "interview_scheduled", label: "Interview" },
  { status: "interview_completed", label: "Completed" },
  { status: "offer", label: "Offer" },
  { status: "rejected", label: "Rejected" },
];

interface KanbanBoardProps {
  applications: JobApplication[];
  onStatusChange?: (applicationId: string, status: ApplicationStatus) => void;
}

export function KanbanBoard({ applications, onStatusChange }: KanbanBoardProps) {
  return (
    <div className="flex gap-4 overflow-x-auto pb-4">
      {KANBAN_COLUMNS.map((column) => {
        const columnApps = applications.filter((app) => app.status === column.status);
        return (
          <div key={column.status} className="min-w-[220px] flex-1">
            <div className="mb-2 flex items-center justify-between">
              <h3 className="text-sm font-semibold">{column.label}</h3>
              <span className="rounded-full bg-muted px-2 py-0.5 text-xs tabular-nums">
                {columnApps.length}
              </span>
            </div>
            <div className="space-y-2">
              {columnApps.map((app) => (
                <Card key={app.id} className="shadow-sm">
                  <CardHeader className="space-y-1 p-3 pb-0">
                    <CardTitle className="text-sm leading-tight">
                      <Link
                        href={`${ROUTES.jobs}/${app.id}`}
                        className="hover:underline"
                      >
                        {app.role_title}
                      </Link>
                    </CardTitle>
                    <p className="text-xs text-muted-foreground">{app.company_name}</p>
                  </CardHeader>
                  <CardContent className="space-y-2 p-3 pt-2">
                    <StatusBadge status={app.status} />
                    {onStatusChange && (
                      <select
                        className="w-full rounded border bg-background px-2 py-1 text-xs"
                        value={app.status}
                        onChange={(e) =>
                          onStatusChange(app.id, e.target.value as ApplicationStatus)
                        }
                        aria-label={`Update status for ${app.company_name}`}
                      >
                        {KANBAN_COLUMNS.map((col) => (
                          <option key={col.status} value={col.status}>
                            {col.label}
                          </option>
                        ))}
                        <option value="withdrawn">Withdrawn</option>
                      </select>
                    )}
                  </CardContent>
                </Card>
              ))}
              {columnApps.length === 0 && (
                <p className="rounded-md border border-dashed p-4 text-center text-xs text-muted-foreground">
                  No applications
                </p>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}
