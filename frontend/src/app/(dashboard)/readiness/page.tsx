"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { LearningRecommendations } from "@/components/career-coach/learning-recommendations";
import { ReadinessScoreCard } from "@/components/career-coach/readiness-score-card";
import { WeakAreasPanel } from "@/components/career-coach/weak-areas-panel";
import { DashboardShell } from "@/components/layout/dashboard-shell";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ROUTES } from "@/constants/routes";
import { useAuth } from "@/hooks/use-auth";
import { hasAccessToken } from "@/lib/auth/tokens";
import { careerCoachService } from "@/services/api/career-coach.service";
import type { ReadinessScore } from "@/types/career-coach";

const categoryLabels: Record<string, string> = {
  resume_ats: "Resume & ATS",
  skills_match: "Skills match",
  interview_prep: "Interview prep",
  job_tracker: "Job tracker",
  roadmap_progress: "Roadmap progress",
};

export default function ReadinessPage() {
  const router = useRouter();
  const { isAuthenticated } = useAuth();
  const [readiness, setReadiness] = useState<ReadinessScore | null>(null);
  const [loading, setLoading] = useState(true);
  const [computing, setComputing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadReadiness = useCallback(async () => {
    if (!hasAccessToken()) {
      setLoading(false);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const data = await careerCoachService.getReadiness();
      setReadiness(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load readiness score");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (!isAuthenticated) {
      router.replace(ROUTES.login);
      return;
    }
    void loadReadiness();
  }, [isAuthenticated, loadReadiness, router]);

  const handleCompute = async () => {
    setComputing(true);
    try {
      const data = await careerCoachService.computeReadiness();
      setReadiness(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to compute readiness");
    } finally {
      setComputing(false);
    }
  };

  return (
    <DashboardShell
      title="Placement readiness"
      description="Detailed breakdown of your placement readiness score"
    >
      <div className="mb-4 flex flex-wrap gap-2">
        <Button onClick={() => void handleCompute()} disabled={computing || loading}>
          {computing ? "Computing…" : "Recompute score"}
        </Button>
        <Button variant="outline" asChild>
          <Link href={ROUTES.careerCoach}>Career coach</Link>
        </Button>
      </div>

      {error && (
        <p className="mb-4 text-sm text-destructive" role="alert">
          {error}
        </p>
      )}

      {loading && !readiness ? (
        <p className="text-sm text-muted-foreground">Loading…</p>
      ) : readiness ? (
        <>
          <ReadinessScoreCard score={readiness.overall_score} />

          <Card className="mt-6">
            <CardHeader>
              <CardTitle>Category breakdown</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {Object.entries(readiness.category_scores).map(([key, value]) => (
                <div key={key}>
                  <div className="mb-1 flex justify-between text-sm">
                    <span>{categoryLabels[key] ?? key}</span>
                    <span className="font-medium">{value}%</span>
                  </div>
                  <div className="h-2 overflow-hidden rounded-full bg-muted">
                    <div className="h-full bg-primary" style={{ width: `${value}%` }} />
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>

          {readiness.missing_skills.length > 0 && (
            <Card className="mt-6">
              <CardHeader>
                <CardTitle>Missing skills</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2">
                  {readiness.missing_skills.map((skill) => (
                    <span
                      key={skill}
                      className="rounded-full bg-muted px-3 py-1 text-sm capitalize"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          <div className="mt-6 grid gap-6 lg:grid-cols-2">
            <WeakAreasPanel weakAreas={readiness.weak_areas} />
            <LearningRecommendations recommendations={readiness.recommendations} />
          </div>

          <p className="mt-4 text-xs text-muted-foreground">
            Last computed: {new Date(readiness.computed_at).toLocaleString()}
          </p>
        </>
      ) : null}
    </DashboardShell>
  );
}
