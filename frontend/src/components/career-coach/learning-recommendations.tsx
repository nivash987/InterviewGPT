"use client";

import { BookOpen, Code, FileText } from "lucide-react";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import type { LearningRecommendation } from "@/types/career-coach";

interface LearningRecommendationsProps {
  recommendations: LearningRecommendation[];
}

const typeIcons: Record<string, typeof BookOpen> = {
  course: BookOpen,
  practice: Code,
  guide: FileText,
};

const priorityBadge: Record<string, string> = {
  high: "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300",
  medium: "bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-300",
  low: "bg-slate-100 text-slate-800 dark:bg-slate-800 dark:text-slate-300",
};

export function LearningRecommendations({ recommendations }: LearningRecommendationsProps) {
  if (recommendations.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Recommended learning</CardTitle>
          <CardDescription>Personalized next steps</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            Compute your readiness score to get learning recommendations.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Recommended learning</CardTitle>
        <CardDescription>Prioritized actions to improve placement readiness</CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        {recommendations.map((rec, idx) => {
          const Icon = typeIcons[rec.resource_type] ?? BookOpen;
          return (
            <div key={`${rec.title}-${idx}`} className="flex gap-3 rounded-lg border p-3">
              <Icon className="mt-0.5 h-5 w-5 shrink-0 text-muted-foreground" />
              <div className="min-w-0 flex-1">
                <div className="flex flex-wrap items-center gap-2">
                  <p className="font-medium">{rec.title}</p>
                  <span
                    className={`rounded px-1.5 py-0.5 text-xs font-medium ${priorityBadge[rec.priority] ?? priorityBadge.low}`}
                  >
                    {rec.priority}
                  </span>
                </div>
                <p className="mt-1 text-sm text-muted-foreground">{rec.description}</p>
                <p className="mt-1 text-xs text-muted-foreground capitalize">
                  {rec.resource_type} · {rec.skill}
                </p>
              </div>
            </div>
          );
        })}
      </CardContent>
    </Card>
  );
}
