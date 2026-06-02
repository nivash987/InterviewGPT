"use client";

import { AlertTriangle, MessageSquare, ThumbsUp } from "lucide-react";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import type { InterviewAnswer, InterviewQuestion } from "@/types/interview";

interface InterviewFeedbackPanelProps {
  strengths: string[];
  improvements: string[];
  questions?: InterviewQuestion[];
}

export function InterviewFeedbackPanel({
  strengths,
  improvements,
  questions = [],
}: InterviewFeedbackPanelProps) {
  const answered = questions.filter((q) => q.answer);

  return (
    <div className="space-y-6">
      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <ThumbsUp className="h-4 w-4 text-green-600" />
              Strengths
            </CardTitle>
            <CardDescription>What you did well in this interview</CardDescription>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2 text-sm">
              {strengths.map((item, i) => (
                <li key={i} className="flex gap-2">
                  <ThumbsUp className="mt-0.5 h-4 w-4 shrink-0 text-green-600" />
                  {item}
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <AlertTriangle className="h-4 w-4 text-amber-600" />
              Areas to improve
            </CardTitle>
            <CardDescription>Focus topics for your next practice session</CardDescription>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2 text-sm">
              {improvements.map((item, i) => (
                <li key={i} className="flex gap-2">
                  <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-amber-600" />
                  {item}
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      </div>

      {answered.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <MessageSquare className="h-4 w-4" />
              Per-question feedback
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {answered.map((q) => (
              <PerQuestionFeedback key={q.id} question={q.question} answer={q.answer!} />
            ))}
          </CardContent>
        </Card>
      )}
    </div>
  );
}

function PerQuestionFeedback({
  question,
  answer,
}: {
  question: string;
  answer: InterviewAnswer;
}) {
  return (
    <div className="rounded-lg border p-4">
      <p className="text-sm font-medium">{question}</p>
      <p className="mt-2 text-sm text-muted-foreground line-clamp-2">{answer.answer}</p>
      <div className="mt-2 flex items-center gap-2">
        <span className="text-sm font-semibold">Score: {answer.score}%</span>
      </div>
      <p className="mt-2 text-sm">{answer.feedback}</p>
    </div>
  );
}
