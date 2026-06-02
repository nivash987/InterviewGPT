"use client";

import { CheckCircle2, Circle, Loader2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import type { CareerRoadmap } from "@/types/career-coach";

interface CareerRoadmapProps {
  roadmap: CareerRoadmap | null;
  onCompleteMilestone?: (milestoneId: string) => void;
  loading?: boolean;
}

function statusIcon(status: string) {
  if (status === "completed") return <CheckCircle2 className="h-5 w-5 text-green-600" />;
  if (status === "in_progress") return <Loader2 className="h-5 w-5 animate-spin text-blue-600" />;
  return <Circle className="h-5 w-5 text-muted-foreground" />;
}

export function CareerRoadmapView({ roadmap, onCompleteMilestone, loading }: CareerRoadmapProps) {
  if (!roadmap) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Career roadmap</CardTitle>
          <CardDescription>Generate a personalized roadmap from your goal</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">No active roadmap yet.</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>{roadmap.title}</CardTitle>
        <CardDescription>
          {roadmap.progress_percent}% complete · {roadmap.target_role}
        </CardDescription>
        <div className="mt-2 h-2 overflow-hidden rounded-full bg-muted">
          <div
            className="h-full bg-primary transition-all"
            style={{ width: `${roadmap.progress_percent}%` }}
          />
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {roadmap.milestones
          .sort((a, b) => a.order - b.order)
          .map((milestone) => (
            <div
              key={milestone.id}
              className="flex gap-4 rounded-lg border p-4"
            >
              <div className="mt-0.5">{statusIcon(milestone.status)}</div>
              <div className="flex-1 space-y-1">
                <p className="font-medium">{milestone.title}</p>
                <p className="text-sm text-muted-foreground">{milestone.description}</p>
                <p className="text-xs text-muted-foreground">
                  ~{milestone.estimated_weeks} weeks
                  {milestone.skills.length > 0 && ` · ${milestone.skills.join(", ")}`}
                </p>
                {milestone.status !== "completed" && onCompleteMilestone && (
                  <Button
                    size="sm"
                    variant="outline"
                    disabled={loading}
                    onClick={() => onCompleteMilestone(milestone.id)}
                  >
                    Mark complete
                  </Button>
                )}
              </div>
            </div>
          ))}
      </CardContent>
    </Card>
  );
}
