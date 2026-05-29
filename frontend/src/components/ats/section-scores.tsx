"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { SECTION_LABELS, type SectionScores } from "@/types/ats";

interface SectionScoresPanelProps {
  scores: SectionScores;
}

export function SectionScoresPanel({ scores }: SectionScoresPanelProps) {
  const entries = Object.entries(scores) as [keyof SectionScores, number][];

  return (
    <Card>
      <CardHeader>
        <CardTitle>Section Scores</CardTitle>
        <CardDescription>Breakdown by resume section</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {entries.map(([key, value]) => (
          <div key={key} className="space-y-1.5">
            <div className="flex items-center justify-between text-sm">
              <span>{SECTION_LABELS[key]}</span>
              <span className="font-medium tabular-nums">{value}%</span>
            </div>
            <Progress value={value} className="h-2" />
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
