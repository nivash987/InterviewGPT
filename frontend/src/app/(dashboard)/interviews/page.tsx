"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { MessageSquare } from "lucide-react";

import { AnswerEditor } from "@/components/interview/answer-editor";
import { InterviewAnalyticsPanel } from "@/components/interview/interview-analytics";
import { InterviewFeedbackPanel } from "@/components/interview/feedback-panel";
import { InterviewHistoryTable } from "@/components/interview/interview-history-table";
import { InterviewSetup } from "@/components/interview/interview-setup";
import { ProgressTracker } from "@/components/interview/progress-tracker";
import { QuestionCard } from "@/components/interview/question-card";
import { ScoreSummary } from "@/components/interview/score-summary";
import { DashboardShell } from "@/components/layout/dashboard-shell";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { ROUTES } from "@/constants/routes";
import { useAuth } from "@/hooks/use-auth";
import { hasAccessToken } from "@/lib/auth/tokens";
import { getErrorMessage } from "@/lib/errors";
import { interviewsService } from "@/services/api/interviews.service";
import { resumesService } from "@/services/api/resumes.service";
import type {
  DifficultyLevel,
  InterviewHistoryItem,
  InterviewPhase,
  InterviewSession,
  InterviewSummary,
  QuestionCountOption,
  InterviewAnalytics,
} from "@/types/interview";
import type { Resume } from "@/types/resume";

export default function InterviewsPage() {
  const router = useRouter();
  const { isAuthenticated } = useAuth();

  const [phase, setPhase] = useState<InterviewPhase>("setup");
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [history, setHistory] = useState<InterviewHistoryItem[]>([]);

  const [selectedResumeId, setSelectedResumeId] = useState<string | null>(null);
  const [role, setRole] = useState("Software Engineer");
  const [difficulty, setDifficulty] = useState<DifficultyLevel>("medium");
  const [questionCount, setQuestionCount] = useState<QuestionCountOption>(10);

  const [session, setSession] = useState<InterviewSession | null>(null);
  const [summary, setSummary] = useState<InterviewSummary | null>(null);
  const [analytics, setAnalytics] = useState<InterviewAnalytics | null>(null);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answerDraft, setAnswerDraft] = useState("");

  const [loadingResumes, setLoadingResumes] = useState(true);
  const [loadingHistory, setLoadingHistory] = useState(true);
  const [starting, setStarting] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [finishing, setFinishing] = useState(false);
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
      if (data.items.length > 0 && !selectedResumeId) {
        setSelectedResumeId(data.items[0].id);
      }
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoadingResumes(false);
    }
  }, [selectedResumeId]);

  const loadHistory = useCallback(async () => {
    if (!hasAccessToken()) {
      setHistory([]);
      setLoadingHistory(false);
      return;
    }
    setLoadingHistory(true);
    try {
      const data = await interviewsService.getHistory();
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

  const answeredCount = useMemo(() => {
    if (!session) return 0;
    return session.questions.filter((q) => q.answer).length;
  }, [session]);

  const currentQuestion = session?.questions[currentIndex] ?? null;

  const handleStart = async () => {
    if (!selectedResumeId || !role.trim()) return;
    setStarting(true);
    setError(null);
    try {
      const result = await interviewsService.start({
        resume_id: selectedResumeId,
        role: role.trim(),
        difficulty,
        question_count: questionCount,
      });
      setSession(result.session);
      setCurrentIndex(result.current_question_index);
      setAnswerDraft("");
      setSummary(null);
      setAnalytics(null);
      setPhase("active");
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setStarting(false);
    }
  };

  const handleSubmitAnswer = async () => {
    if (!session || !currentQuestion || !answerDraft.trim()) return;
    setSubmitting(true);
    setError(null);
    try {
      await interviewsService.submitAnswer(
        session.id,
        currentQuestion.id,
        answerDraft.trim(),
      );

      const detail = await interviewsService.getSession(session.id);
      setSession(detail.session);

      const nextIndex = Math.min(
        currentIndex + 1,
        detail.session.questions.length - 1,
      );
      setCurrentIndex(nextIndex);
      setAnswerDraft(detail.session.questions[nextIndex]?.answer?.answer ?? "");
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setSubmitting(false);
    }
  };

  const handleFinish = async (sessionId?: string) => {
    const id = sessionId ?? session?.id;
    if (!id) return;
    setFinishing(true);
    setError(null);
    try {
      const result = await interviewsService.finish(id);
      setSession(result.session);
      setSummary(result.summary);
      const detail = await interviewsService.getSession(id);
      setAnalytics(detail.analytics);
      setPhase("results");
      await loadHistory();
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setFinishing(false);
    }
  };

  const handleViewHistory = async (sessionId: string) => {
    setError(null);
    try {
      const detail = await interviewsService.getSession(sessionId);
      setSession(detail.session);
      setSummary(detail.summary);
      setAnalytics(detail.analytics);
      if (detail.session.status === "completed") {
        setPhase("results");
      } else {
        const firstUnanswered = detail.session.questions.findIndex((q) => !q.answer);
        setCurrentIndex(firstUnanswered >= 0 ? firstUnanswered : 0);
        setAnswerDraft(detail.session.questions[firstUnanswered]?.answer?.answer ?? "");
        setPhase("active");
      }
    } catch (err) {
      setError(getErrorMessage(err));
    }
  };

  const resetToSetup = () => {
    setPhase("setup");
    setSession(null);
    setSummary(null);
    setAnalytics(null);
    setCurrentIndex(0);
    setAnswerDraft("");
  };

  return (
    <DashboardShell
      title="Mock Interviews"
      description="Practice with rule-based questions tailored to your resume and ATS profile"
    >
      <div className="mx-auto max-w-5xl space-y-6">
        <div className="flex flex-wrap gap-2">
          <Button
            variant={phase === "setup" ? "default" : "outline"}
            size="sm"
            onClick={() => setPhase("setup")}
          >
            Setup
          </Button>
          {session && phase !== "setup" && (
            <Button
              variant={phase === "active" ? "default" : "outline"}
              size="sm"
              onClick={() => setPhase("active")}
              disabled={session.status === "completed"}
            >
              Active interview
            </Button>
          )}
          {summary && (
            <Button
              variant={phase === "results" ? "default" : "outline"}
              size="sm"
              onClick={() => setPhase("results")}
            >
              Results
            </Button>
          )}
          <Button
            variant={phase === "history" ? "default" : "outline"}
            size="sm"
            onClick={() => setPhase("history")}
          >
            History
          </Button>
        </div>

        {error && (
          <div className="rounded-lg border border-destructive/50 bg-destructive/10 px-4 py-3 text-sm text-destructive">
            {error}
          </div>
        )}

        {phase === "setup" && (
          <InterviewSetup
            resumes={resumes}
            selectedResumeId={selectedResumeId}
            onResumeChange={setSelectedResumeId}
            role={role}
            onRoleChange={setRole}
            difficulty={difficulty}
            onDifficultyChange={setDifficulty}
            questionCount={questionCount}
            onQuestionCountChange={setQuestionCount}
            onStart={handleStart}
            starting={starting}
            loadingResumes={loadingResumes}
          />
        )}

        {phase === "active" && session && currentQuestion && (
          <div className="space-y-6">
            <ProgressTracker
              current={answeredCount}
              total={session.questions.length}
            />

            <QuestionCard
              question={currentQuestion}
              index={currentIndex}
              total={session.questions.length}
            />

            <Card>
              <CardContent className="pt-6">
                <AnswerEditor
                  value={answerDraft}
                  onChange={setAnswerDraft}
                  onSubmit={() => void handleSubmitAnswer()}
                  submitting={submitting}
                  disabled={session.status === "completed"}
                  lastScore={currentQuestion.answer?.score ?? null}
                />
              </CardContent>
            </Card>

            <div className="flex flex-wrap gap-2">
              <Button
                variant="outline"
                size="sm"
                disabled={currentIndex === 0}
                onClick={() => {
                  setCurrentIndex((i) => Math.max(0, i - 1));
                  const q = session.questions[Math.max(0, currentIndex - 1)];
                  setAnswerDraft(q?.answer?.answer ?? "");
                }}
              >
                Previous
              </Button>
              <Button
                variant="outline"
                size="sm"
                disabled={currentIndex >= session.questions.length - 1}
                onClick={() => {
                  const next = Math.min(session.questions.length - 1, currentIndex + 1);
                  setCurrentIndex(next);
                  setAnswerDraft(session.questions[next]?.answer?.answer ?? "");
                }}
              >
                Next
              </Button>
              <Button
                variant="secondary"
                size="sm"
                onClick={() => void handleFinish()}
                disabled={finishing || answeredCount === 0}
              >
                {finishing ? "Finishing..." : "Finish interview"}
              </Button>
            </div>
          </div>
        )}

        {phase === "results" && summary && session && (
          <div className="space-y-6">
            <ScoreSummary summary={summary} />
            <InterviewFeedbackPanel
              strengths={summary.strengths}
              improvements={summary.improvements}
              questions={session.questions}
            />
            {analytics && <InterviewAnalyticsPanel analytics={analytics} />}
            <Button onClick={resetToSetup}>Start new interview</Button>
          </div>
        )}

        {phase === "history" && (
          <InterviewHistoryTable
            items={history}
            loading={loadingHistory}
            onView={(id) => void handleViewHistory(id)}
          />
        )}

        {phase === "setup" && (
          <Card>
            <CardContent className="flex items-start gap-3 pt-6">
              <MessageSquare className="mt-0.5 h-5 w-5 text-muted-foreground" />
              <p className="text-sm text-muted-foreground">
                Run an ATS analysis on your resume first for stronger, gap-focused interview
                questions. Scoring is rule-based using keyword coverage, answer length, and
                structure.
              </p>
            </CardContent>
          </Card>
        )}

        {phase !== "history" && phase !== "setup" && (
          <InterviewHistoryTable
            items={history}
            loading={loadingHistory}
            onView={(id) => void handleViewHistory(id)}
          />
        )}
      </div>
    </DashboardShell>
  );
}
