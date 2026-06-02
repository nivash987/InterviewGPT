"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { CareerRoadmapView } from "@/components/career-coach/career-roadmap";
import { DashboardShell } from "@/components/layout/dashboard-shell";
import { Button } from "@/components/ui/button";
import { ROUTES } from "@/constants/routes";
import { useAuth } from "@/hooks/use-auth";
import { hasAccessToken } from "@/lib/auth/tokens";
import { careerCoachService } from "@/services/api/career-coach.service";
import type { CareerRoadmap } from "@/types/career-coach";

export default function RoadmapPage() {
  const router = useRouter();
  const { isAuthenticated } = useAuth();
  const [roadmap, setRoadmap] = useState<CareerRoadmap | null>(null);
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadRoadmap = useCallback(async () => {
    if (!hasAccessToken()) {
      setLoading(false);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const data = await careerCoachService.getRoadmap();
      setRoadmap(data);
    } catch {
      setRoadmap(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (!isAuthenticated) {
      router.replace(ROUTES.login);
      return;
    }
    void loadRoadmap();
  }, [isAuthenticated, loadRoadmap, router]);

  const handleGenerate = async () => {
    setLoading(true);
    try {
      const data = await careerCoachService.generateRoadmap();
      setRoadmap(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to generate roadmap");
    } finally {
      setLoading(false);
    }
  };

  const handleCompleteMilestone = async (milestoneId: string) => {
    setUpdating(true);
    try {
      await careerCoachService.updateProgress(milestoneId, { status: "completed" });
      await loadRoadmap();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update progress");
    } finally {
      setUpdating(false);
    }
  };

  return (
    <DashboardShell
      title="Career roadmap"
      description="Track milestones on your path to placement"
    >
      <div className="mb-4 flex flex-wrap gap-2">
        <Button onClick={() => void handleGenerate()} disabled={loading}>
          {roadmap ? "Regenerate roadmap" : "Generate roadmap"}
        </Button>
        <Button variant="outline" asChild>
          <Link href={ROUTES.careerCoach}>Back to career coach</Link>
        </Button>
      </div>

      {error && (
        <p className="mb-4 text-sm text-destructive" role="alert">
          {error}
        </p>
      )}

      {loading && !roadmap ? (
        <p className="text-sm text-muted-foreground">Loading roadmap…</p>
      ) : (
        <CareerRoadmapView
          roadmap={roadmap}
          loading={updating}
          onCompleteMilestone={(id) => void handleCompleteMilestone(id)}
        />
      )}
    </DashboardShell>
  );
}
