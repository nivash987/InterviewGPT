"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { BarChart3 } from "lucide-react";

import { AnalysisHistoryTable } from "@/components/ats/analysis-history";
import { AtsCharts } from "@/components/ats/ats-charts";
import { FeedbackPanel } from "@/components/ats/feedback-panel";
import { RecommendedRolesPanel } from "@/components/ats/recommended-roles";
import { ResumeSelector } from "@/components/ats/resume-selector";
import { AtsScoreCard, CompletenessScoreCard } from "@/components/ats/score-cards";
import { SectionScoresPanel } from "@/components/ats/section-scores";
import { SkillsPanel } from "@/components/ats/skills-panel";
import { DashboardShell } from "@/components/layout/dashboard-shell";
import { Card, CardContent } from "@/components/ui/card";
import { ROUTES } from "@/constants/routes";
import { useAuth } from "@/hooks/use-auth";
import { hasAccessToken } from "@/lib/auth/tokens";
import { getErrorMessage } from "@/lib/errors";
import { atsService } from "@/services/api/ats.service";
import { resumesService } from "@/services/api/resumes.service";
import type { AtsAnalysisResult, AtsHistoryItem } from "@/types/ats";
import type { Resume } from "@/types/resume";

export default function AtsPage() {
  const router = useRouter();
  const { isAuthenticated } = useAuth();

  const [resumes, setResumes] = useState<Resume[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [analysis, setAnalysis] = useState<AtsAnalysisResult | null>(null);
  const [history, setHistory] = useState<AtsHistoryItem[]>([]);

  const [loadingResumes, setLoadingResumes] = useState(true);
  const [loadingHistory, setLoadingHistory] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadResumes = useCallback(async () => {
    if (!hasAccessToken()) {
      setResumes([]);
      setLoadingResumes(false);
      return;
    }
    setLoadingResumes(true);
    try {
      const data = await resumesService.list();
      setResumes(data.items);
      if (data.items.length > 0 && !selectedId) {
        setSelectedId(data.items[0].id);
      }
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoadingResumes(false);
    }
  }, [selectedId]);

  const loadHistory = useCallback(async () => {
    if (!hasAccessToken()) {
      setHistory([]);
      setLoadingHistory(false);
      return;
    }
    setLoadingHistory(true);
    try {
      const data = await atsService.getHistory();
      setHistory(data.items);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoadingHistory(false);
    }
  }, []);

  useEffect(() => {
    if (!isAuthenticated) {
      router.replace(ROUTES.login);
      return;
    }
    void loadResumes();
    void loadHistory();
  }, [isAuthenticated, loadResumes, loadHistory, router]);

  const handleAnalyze = async () => {
    if (!selectedId) return;
    setAnalyzing(true);
    setError(null);
    try {
      const result = await atsService.analyze(selectedId);
      setAnalysis(result);
      await loadHistory();
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setAnalyzing(false);
    }
  };

  const handleSelect = async (id: string) => {
    setSelectedId(id);
    setError(null);
    try {
      const latest = await atsService.getLatest(id);
      setAnalysis(latest);
    } catch {
      setAnalysis(null);
    }
  };

  return (
    <DashboardShell
      title="ATS Analysis"
      description="Rule-based resume scoring, skill extraction, and role recommendations."
    >
      <div className="mx-auto max-w-6xl space-y-6">
        {error && (
          <p className="rounded-md border border-destructive/50 bg-destructive/10 px-4 py-2 text-sm text-destructive">
            {error}
          </p>
        )}

        <ResumeSelector
          resumes={resumes}
          selectedId={selectedId}
          onSelect={(id) => void handleSelect(id)}
          onAnalyze={() => void handleAnalyze()}
          analyzing={analyzing}
          loading={loadingResumes}
        />

        {!analysis && !analyzing && (
          <Card>
            <CardContent className="flex flex-col items-center justify-center gap-3 py-16 text-center">
              <BarChart3 className="h-12 w-12 text-muted-foreground" />
              <p className="text-lg font-medium">No analysis yet</p>
              <p className="max-w-md text-sm text-muted-foreground">
                Select an uploaded resume and click Analyze to generate your ATS report with scores,
                skill gaps, and role recommendations.
              </p>
            </CardContent>
          </Card>
        )}

        {analysis && (
          <>
            <div className="grid gap-4 sm:grid-cols-2">
              <AtsScoreCard score={analysis.ats_score} />
              <CompletenessScoreCard score={analysis.completeness_score} />
            </div>

            <AtsCharts history={history} keywordCoverage={analysis.keyword_coverage} />

            <SectionScoresPanel scores={analysis.section_scores} />

            <SkillsPanel
              skillsFound={analysis.skills_found}
              missingSkills={analysis.missing_skills}
            />

            <FeedbackPanel
              strengths={analysis.strengths}
              weaknesses={analysis.weaknesses}
              suggestions={analysis.suggestions}
            />

            <RecommendedRolesPanel roles={analysis.recommended_roles} />
          </>
        )}

        <AnalysisHistoryTable items={history} loading={loadingHistory} />
      </div>
    </DashboardShell>
  );
}
