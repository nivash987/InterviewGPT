"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

import { LearningRecommendations } from "@/components/career-coach/learning-recommendations";
import { ReadinessScoreCard } from "@/components/career-coach/readiness-score-card";
import { WeakAreasPanel } from "@/components/career-coach/weak-areas-panel";
import { DashboardShell } from "@/components/layout/dashboard-shell";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ROUTES } from "@/constants/routes";
import { useAuth } from "@/hooks/use-auth";
import { hasAccessToken } from "@/lib/auth/tokens";
import { careerCoachService } from "@/services/api/career-coach.service";
import type { CareerCoachDashboard } from "@/types/career-coach";

export default function DashboardPage() {
  const { user } = useAuth();
  const [coachDashboard, setCoachDashboard] = useState<CareerCoachDashboard | null>(null);

  const loadCoach = useCallback(async () => {
    if (!hasAccessToken()) return;
    try {
      const data = await careerCoachService.getDashboard();
      setCoachDashboard(data);
    } catch {
      setCoachDashboard(null);
    }
  }, []);

  useEffect(() => {
    void loadCoach();
  }, [loadCoach]);

  return (
    <DashboardShell
      title="Dashboard"
      description="Your preparation hub. More modules will appear here as they ship."
    >
      {coachDashboard && (
        <div className="mb-8 space-y-6">
          <h2 className="text-lg font-semibold">Placement readiness</h2>
          <div className="grid gap-6 lg:grid-cols-3">
            <ReadinessScoreCard
              score={coachDashboard.readiness_score ?? 0}
              trend={coachDashboard.readiness_trend}
            />
            <Card className="lg:col-span-2">
              <CardHeader>
                <CardTitle>Career coach snapshot</CardTitle>
                <CardDescription>
                  {coachDashboard.active_goal
                    ? `Goal: ${coachDashboard.active_goal.target_role}`
                    : "Set a career goal to unlock personalized coaching"}
                </CardDescription>
              </CardHeader>
              <CardContent className="grid gap-4 sm:grid-cols-3 text-sm">
                <div>
                  <p className="text-muted-foreground">Missing skills</p>
                  <p className="text-2xl font-semibold">{coachDashboard.missing_skills.length}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Roadmap progress</p>
                  <p className="text-2xl font-semibold">
                    {coachDashboard.roadmap_progress_percent != null
                      ? `${coachDashboard.roadmap_progress_percent}%`
                      : "—"}
                  </p>
                </div>
                <div>
                  <p className="text-muted-foreground">Skill coverage</p>
                  <p className="text-2xl font-semibold">
                    {coachDashboard.skill_coverage_percent != null
                      ? `${coachDashboard.skill_coverage_percent}%`
                      : "—"}
                  </p>
                </div>
                <Link
                  href={ROUTES.careerCoach}
                  className="sm:col-span-3 inline-flex items-center text-sm font-medium text-primary hover:underline"
                >
                  Open career coach →
                </Link>
              </CardContent>
            </Card>
          </div>
          <div className="grid gap-6 lg:grid-cols-2">
            <WeakAreasPanel weakAreas={coachDashboard.weak_areas} />
            <LearningRecommendations recommendations={coachDashboard.recommendations} />
          </div>
        </div>
      )}

      <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle>Welcome{user?.full_name ? `, ${user.full_name.split(" ")[0]}` : ""}</CardTitle>
            <CardDescription>
              You are signed in as {user?.email ?? "…"}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              Email verified: {user?.is_email_verified ? "Yes" : "Pending verification"}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Mock interviews</CardTitle>
            <CardDescription>Practice with resume-tailored questions</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground mb-4">
              Rule-based mock interviews use your resume skills, ATS gaps, and target role with
              per-question scoring and feedback.
            </p>
            <Link
              href={ROUTES.interviews}
              className="inline-flex items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90"
            >
              Start mock interview
            </Link>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Resumes</CardTitle>
            <CardDescription>Upload and manage your CV</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground mb-4">
              Upload PDF or DOCX resumes with automatic parsing for skills, experience, and education.
            </p>
            <Link
              href={ROUTES.resumes}
              className="inline-flex items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90"
            >
              Manage resumes
            </Link>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Career coach</CardTitle>
            <CardDescription>Placement readiness & roadmap</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground mb-4">
              Get a placement readiness score, skill gap analysis, personalized roadmap, and learning
              recommendations.
            </p>
            <Link
              href={ROUTES.careerCoach}
              className="inline-flex items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90"
            >
              Open career coach
            </Link>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>ATS Analysis</CardTitle>
            <CardDescription>Score and optimize your resume</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground mb-4">
              Run rule-based ATS scoring, skill gap analysis, and role recommendations on uploaded resumes.
            </p>
            <Link
              href={ROUTES.ats}
              className="inline-flex items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90"
            >
              Open ATS dashboard
            </Link>
          </CardContent>
        </Card>
      </div>
    </DashboardShell>
  );
}
