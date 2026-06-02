"use client";

import { TrendingDown, TrendingUp, Minus } from "lucide-react";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";

interface ReadinessScoreCardProps {
  score: number;
  trend?: string | null;
  className?: string;
}

function scoreLabel(score: number): string {
  if (score >= 80) return "Placement ready";
  if (score >= 60) return "Almost ready";
  if (score >= 40) return "Building momentum";
  return "Early stage";
}

function scoreColor(score: number): string {
  if (score >= 80) return "text-green-600";
  if (score >= 60) return "text-blue-600";
  if (score >= 40) return "text-amber-600";
  return "text-red-600";
}

export function ReadinessScoreCard({ score, trend, className }: ReadinessScoreCardProps) {
  const TrendIcon =
    trend === "up" ? TrendingUp : trend === "down" ? TrendingDown : Minus;

  return (
    <Card className={cn(className)}>
      <CardHeader>
        <CardTitle>Placement Readiness</CardTitle>
        <CardDescription>{scoreLabel(score)}</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="flex items-end gap-3">
          <span className={cn("text-5xl font-bold tabular-nums", scoreColor(score))}>{score}</span>
          <span className="mb-2 text-muted-foreground">/ 100</span>
          {trend && (
            <span className="mb-2 flex items-center gap-1 text-sm text-muted-foreground">
              <TrendIcon className="h-4 w-4" />
              {trend === "up" ? "Improving" : trend === "down" ? "Declining" : "Stable"}
            </span>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
