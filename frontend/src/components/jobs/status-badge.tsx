import { cn } from "@/lib/utils";
import type { ApplicationStatus } from "@/types/jobs";

const STATUS_LABELS: Record<ApplicationStatus, string> = {
  applied: "Applied",
  screening: "Screening",
  interview_scheduled: "Interview Scheduled",
  interview_completed: "Interview Done",
  offer: "Offer",
  rejected: "Rejected",
  withdrawn: "Withdrawn",
};

const STATUS_STYLES: Record<ApplicationStatus, string> = {
  applied: "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300",
  screening: "bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-300",
  interview_scheduled: "bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300",
  interview_completed: "bg-indigo-100 text-indigo-800 dark:bg-indigo-900/30 dark:text-indigo-300",
  offer: "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300",
  rejected: "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300",
  withdrawn: "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300",
};

interface StatusBadgeProps {
  status: ApplicationStatus;
  className?: string;
}

export function StatusBadge({ status, className }: StatusBadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium",
        STATUS_STYLES[status] ?? STATUS_STYLES.applied,
        className,
      )}
    >
      {STATUS_LABELS[status] ?? status}
    </span>
  );
}
