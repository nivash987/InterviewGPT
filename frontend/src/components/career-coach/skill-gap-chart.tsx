"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import type { SkillGapAnalysis } from "@/types/career-coach";

interface SkillGapChartProps {
  analysis: SkillGapAnalysis | null;
}

const priorityColors: Record<string, string> = {
  high: "bg-red-500",
  medium: "bg-amber-500",
  low: "bg-slate-400",
};

export function SkillGapChart({ analysis }: SkillGapChartProps) {
  if (!analysis) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Skill gaps</CardTitle>
          <CardDescription>Run analysis to see missing skills</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">No skill gap data yet.</p>
        </CardContent>
      </Card>
    );
  }

  const covered = analysis.coverage_percent;
  const missing = 100 - covered;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Skill coverage</CardTitle>
        <CardDescription>
          {analysis.coverage_percent}% match for {analysis.target_role}
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex h-4 overflow-hidden rounded-full bg-muted">
          <div className="bg-primary transition-all" style={{ width: `${covered}%` }} />
          <div className="bg-muted-foreground/30" style={{ width: `${missing}%` }} />
        </div>
        <div className="flex justify-between text-xs text-muted-foreground">
          <span>Covered ({analysis.user_skills.length})</span>
          <span>Missing ({analysis.missing_skills.length})</span>
        </div>
        <ul className="space-y-2">
          {analysis.missing_skills.slice(0, 8).map((item) => (
            <li key={item.skill_name} className="flex items-center gap-2 text-sm">
              <span
                className={`h-2 w-2 rounded-full ${priorityColors[item.priority] ?? "bg-slate-400"}`}
              />
              <span className="font-medium capitalize">{item.skill_name}</span>
              <span className="text-muted-foreground">({item.priority})</span>
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  );
}
