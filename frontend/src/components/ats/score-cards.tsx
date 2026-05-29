"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { cn } from "@/lib/utils";

interface ScoreCardProps {
  title: string;
  score: number;
  description?: string;
  className?: string;
}

function scoreColor(score: number): string {
  if (score >= 80) return "text-green-600 dark:text-green-400";
  if (score >= 60) return "text-yellow-600 dark:text-yellow-400";
  return "text-destructive";
}

export function ScoreCard({ title, score, description, className }: ScoreCardProps) {
  return (
    <Card className={cn(className)}>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <p className={cn("text-4xl font-bold tabular-nums", scoreColor(score))}>{score}</p>
        <Progress value={score} className="mt-3 h-2" />
        {description && (
          <p className="mt-2 text-xs text-muted-foreground">{description}</p>
        )}
      </CardContent>
    </Card>
  );
}

export function AtsScoreCard({ score }: { score: number }) {
  return (
    <ScoreCard
      title="ATS Score"
      score={score}
      description="Overall compatibility with applicant tracking systems"
    />
  );
}

export function CompletenessScoreCard({ score }: { score: number }) {
  return (
    <ScoreCard
      title="Completeness Score"
      score={score}
      description="How complete your resume sections are"
    />
  );
}
