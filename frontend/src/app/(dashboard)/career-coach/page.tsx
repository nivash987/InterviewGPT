"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { LearningRecommendations } from "@/components/career-coach/learning-recommendations";
import { ProgressDashboard } from "@/components/career-coach/progress-dashboard";
import { ReadinessScoreCard } from "@/components/career-coach/readiness-score-card";
import { SkillGapChart } from "@/components/career-coach/skill-gap-chart";
import { WeakAreasPanel } from "@/components/career-coach/weak-areas-panel";
import { DashboardShell } from "@/components/layout/dashboard-shell";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ROUTES } from "@/constants/routes";
import { useAuth } from "@/hooks/use-auth";
import { hasAccessToken } from "@/lib/auth/tokens";
import { careerCoachService } from "@/services/api/career-coach.service";
import type { CareerCoachDashboard, SkillGapAnalysis } from "@/types/career-coach";

export default function CareerCoachPage() {
  const router = useRouter();
  const { isAuthenticated } = useAuth();
  const [dashboard, setDashboard] = useState<CareerCoachDashboard | null>(null);
  const [skillGaps, setSkillGaps] = useState<SkillGapAnalysis | null>(null);
  const [loading, setLoading] = useState(true);
  const [computing, setComputing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [targetRole, setTargetRole] = useState("Software Engineer");
  const [timelineMonths, setTimelineMonths] = useState("6");

  const loadData = useCallback(async () => {
    if (!hasAccessToken()) {
      setLoading(false);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const [dash, gaps] = await Promise.all([
        careerCoachService.getDashboard(),
        careerCoachService.getSkillGaps(),
      ]);
      setDashboard(dash);
      setSkillGaps(gaps);
      if (dash.active_goal) {
        setTargetRole(dash.active_goal.target_role);
        setTimelineMonths(String(dash.active_goal.target_timeline_months ?? 6));
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load career coach data");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (!isAuthenticated) {
      router.replace(ROUTES.login);
      return;
    }
    void loadData();
  }, [isAuthenticated, loadData, router]);

  const handleSetGoal = async () => {
    try {
      await careerCoachService.setGoal({
        target_role: targetRole,
        target_timeline_months: Number(timelineMonths) || 6,
      });
      await loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to set goal");
    }
  };

  const handleComputeReadiness = async () => {
    setComputing(true);
    try {
      await careerCoachService.computeReadiness();
      await loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to compute readiness");
    } finally {
      setComputing(false);
    }
  };

  const handleGenerateRoadmap = async () => {
    try {
      await careerCoachService.generateRoadmap();
      router.push(ROUTES.roadmap);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to generate roadmap");
    }
  };

  return (
    <DashboardShell
      title="Career Coach"
      description="AI-powered placement readiness, skill gaps, and learning recommendations"
    >
      {error && (
        <p className="mb-4 text-sm text-destructive" role="alert">
          {error}
        </p>
      )}

      <div className="mb-6 flex flex-wrap gap-2">
        <Button variant="outline" asChild>
          <Link href={ROUTES.roadmap}>View roadmap</Link>
        </Button>
        <Button variant="outline" asChild>
          <Link href={ROUTES.readiness}>Readiness details</Link>
        </Button>
        <Button onClick={() => void handleComputeReadiness()} disabled={computing || loading}>
          {computing ? "Computing…" : "Refresh readiness score"}
        </Button>
      </div>

      <ProgressDashboard dashboard={dashboard} />

      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <ReadinessScoreCard
          score={dashboard?.readiness_score ?? 0}
          trend={dashboard?.readiness_trend}
        />
        <SkillGapChart analysis={skillGaps} />
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Career goal</CardTitle>
            <CardDescription>Set your target role to personalize coaching</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="target-role">Target role</Label>
              <Input
                id="target-role"
                value={targetRole}
                onChange={(e) => setTargetRole(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="timeline">Timeline (months)</Label>
              <Input
                id="timeline"
                type="number"
                min={1}
                max={60}
                value={timelineMonths}
                onChange={(e) => setTimelineMonths(e.target.value)}
              />
            </div>
            <div className="flex flex-wrap gap-2">
              <Button onClick={() => void handleSetGoal()}>Save goal</Button>
              <Button variant="secondary" onClick={() => void handleGenerateRoadmap()}>
                Generate roadmap
              </Button>
            </div>
          </CardContent>
        </Card>
        <WeakAreasPanel weakAreas={dashboard?.weak_areas ?? []} />
      </div>

      <div className="mt-6">
        <LearningRecommendations recommendations={dashboard?.recommendations ?? []} />
      </div>
    </DashboardShell>
  );
}
