"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import type { CareerCoachDashboard } from "@/types/career-coach";

interface ProgressDashboardProps {
  dashboard: CareerCoachDashboard | null;
}

export function ProgressDashboard({ dashboard }: ProgressDashboardProps) {
  if (!dashboard) return null;

  const stats = [
    {
      label: "Readiness score",
      value: dashboard.readiness_score != null ? `${dashboard.readiness_score}%` : "—",
    },
    {
      label: "Skill coverage",
      value:
        dashboard.skill_coverage_percent != null ? `${dashboard.skill_coverage_percent}%` : "—",
    },
    {
      label: "Roadmap progress",
      value:
        dashboard.roadmap_progress_percent != null
          ? `${dashboard.roadmap_progress_percent}%`
          : "—",
    },
    {
      label: "Missing skills",
      value: String(dashboard.missing_skills.length),
    },
  ];

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      {stats.map((stat) => (
        <Card key={stat.label}>
          <CardHeader className="pb-2">
            <CardDescription>{stat.label}</CardDescription>
            <CardTitle className="text-2xl">{stat.value}</CardTitle>
          </CardHeader>
          <CardContent />
        </Card>
      ))}
    </div>
  );
}
