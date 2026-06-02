"use client";

import { Progress } from "@/components/ui/progress";

interface ProgressTrackerProps {
  current: number;
  total: number;
  label?: string;
}

export function ProgressTracker({ current, total, label }: ProgressTrackerProps) {
  const percent = total > 0 ? Math.round((current / total) * 100) : 0;

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between text-sm">
        <span className="font-medium text-muted-foreground">
          {label ?? "Interview progress"}
        </span>
        <span className="font-medium">
          {current} / {total} ({percent}%)
        </span>
      </div>
      <Progress value={percent} className="h-2" />
    </div>
  );
}
