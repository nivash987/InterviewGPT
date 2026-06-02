"use client";

import { Award, CheckCircle2 } from "lucide-react";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import type { InterviewSummary } from "@/types/interview";

interface ScoreSummaryProps {
  summary: InterviewSummary;
}

export function ScoreSummary({ summary }: ScoreSummaryProps) {
  return (
    <div className="grid gap-4 md:grid-cols-2">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Award className="h-5 w-5 text-primary" />
            Overall score
          </CardTitle>
          <CardDescription>
            {summary.questions_answered} of {summary.total_questions} questions answered
          </CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-4xl font-bold">{summary.total_score}%</p>
          <Progress value={summary.total_score} className="mt-4 h-2" />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <CheckCircle2 className="h-4 w-4" />
            Category breakdown
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {summary.category_breakdown.map((item) => (
            <div key={item.category} className="space-y-1">
              <div className="flex justify-between text-sm">
                <span>{item.category}</span>
                <span className="font-medium">{item.average_score}%</span>
              </div>
              <Progress value={item.average_score} className="h-1.5" />
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}
