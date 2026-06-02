"use client";

import { AlertTriangle } from "lucide-react";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import type { WeaknessItem } from "@/types/career-coach";

interface WeakAreasPanelProps {
  weakAreas: WeaknessItem[];
}

const severityStyles: Record<string, string> = {
  high: "border-red-200 bg-red-50/50 dark:border-red-900 dark:bg-red-950/20",
  medium: "border-amber-200 bg-amber-50/50 dark:border-amber-900 dark:bg-amber-950/20",
  low: "border-slate-200 bg-slate-50/50 dark:border-slate-800 dark:bg-slate-950/20",
};

export function WeakAreasPanel({ weakAreas }: WeakAreasPanelProps) {
  if (weakAreas.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Weak areas</CardTitle>
          <CardDescription>Focus areas to improve readiness</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">No significant weak areas detected.</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Weak areas</CardTitle>
        <CardDescription>Focus areas to improve readiness</CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        {weakAreas.map((area) => (
          <div
            key={area.area}
            className={`rounded-lg border p-3 ${severityStyles[area.severity] ?? severityStyles.low}`}
          >
            <div className="flex items-start gap-2">
              <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />
              <div>
                <p className="font-medium">
                  {area.area}
                  <span className="ml-2 text-xs font-normal text-muted-foreground">
                    ({area.severity})
                  </span>
                </p>
                <p className="mt-1 text-sm text-muted-foreground">{area.description}</p>
                <p className="mt-2 text-sm">{area.suggested_action}</p>
              </div>
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
