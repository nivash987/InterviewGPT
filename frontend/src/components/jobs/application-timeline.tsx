"use client";

import { StatusBadge } from "@/components/jobs/status-badge";
import type { ApplicationStatus, StatusHistoryEvent } from "@/types/jobs";

interface ApplicationTimelineProps {
  events: StatusHistoryEvent[];
}

function formatDate(iso: string): string {
  return new Date(iso).toLocaleString(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

export function ApplicationTimeline({ events }: ApplicationTimelineProps) {
  if (events.length === 0) {
    return <p className="text-sm text-muted-foreground">No timeline events yet.</p>;
  }

  return (
    <ol className="relative space-y-6 border-l border-border pl-6">
      {events.map((event) => (
        <li key={event.id} className="relative">
          <span className="absolute -left-[1.6rem] top-1.5 h-3 w-3 rounded-full border-2 border-primary bg-background" />
          <div className="space-y-1">
            <div className="flex flex-wrap items-center gap-2">
              {event.from_status && (
                <>
                  <StatusBadge status={event.from_status as ApplicationStatus} />
                  <span className="text-muted-foreground">→</span>
                </>
              )}
              <StatusBadge status={event.to_status as ApplicationStatus} />
            </div>
            <p className="text-xs text-muted-foreground">{formatDate(event.created_at)}</p>
            {event.note && <p className="text-sm">{event.note}</p>}
          </div>
        </li>
      ))}
    </ol>
  );
}
