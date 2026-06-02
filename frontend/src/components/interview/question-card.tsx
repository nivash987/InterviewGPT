"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import type { InterviewQuestion } from "@/types/interview";

interface QuestionCardProps {
  question: InterviewQuestion;
  index: number;
  total: number;
}

export function QuestionCard({ question, index, total }: QuestionCardProps) {
  return (
    <Card>
      <CardHeader>
        <div className="flex flex-wrap items-center gap-2">
          <CardDescription>
            Question {index + 1} of {total}
          </CardDescription>
          <span className="rounded-md bg-secondary px-2 py-0.5 text-xs font-medium">
            {question.category}
          </span>
          <span className="rounded-md border px-2 py-0.5 text-xs font-medium capitalize">
            {question.difficulty}
          </span>
        </div>
        <CardTitle className="text-lg leading-relaxed">{question.question}</CardTitle>
      </CardHeader>
      {question.expected_keywords.length > 0 && (
        <CardContent>
          <p className="mb-2 text-xs font-medium uppercase tracking-wide text-muted-foreground">
            Topics to cover
          </p>
          <div className="flex flex-wrap gap-1.5">
            {question.expected_keywords.slice(0, 8).map((keyword) => (
              <span
                key={keyword}
                className={cn(
                  "rounded-md border px-2 py-0.5 text-xs text-muted-foreground",
                )}
              >
                {keyword}
              </span>
            ))}
          </div>
        </CardContent>
      )}
    </Card>
  );
}
