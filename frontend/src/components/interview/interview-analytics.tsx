"use client";

import { TrendingDown, TrendingUp } from "lucide-react";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import type { InterviewAnalytics } from "@/types/interview";

interface InterviewAnalyticsProps {
  analytics: InterviewAnalytics;
}

export function InterviewAnalyticsPanel({ analytics }: InterviewAnalyticsProps) {
  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Interview score trend</CardTitle>
          <CardDescription>Your scores across completed mock interviews</CardDescription>
        </CardHeader>
        <CardContent>
          {analytics.score_trend.length === 0 ? (
            <p className="text-sm text-muted-foreground">Complete more interviews to see trends.</p>
          ) : (
            <div className="space-y-2">
              {analytics.score_trend.map((point) => (
                <div
                  key={point.session_id}
                  className="flex items-center justify-between rounded-md border px-3 py-2 text-sm"
                >
                  <span>{point.role}</span>
                  <span className="font-semibold">{point.total_score}%</span>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <TrendingUp className="h-4 w-4 text-green-600" />
              Strong topics
            </CardTitle>
          </CardHeader>
          <CardContent>
            {analytics.strong_topics.length === 0 ? (
              <p className="text-sm text-muted-foreground">No strong topics yet.</p>
            ) : (
              <ul className="space-y-2 text-sm">
                {analytics.strong_topics.map((topic) => (
                  <li key={topic.category} className="flex justify-between">
                    <span>{topic.category}</span>
                    <span className="font-medium">{topic.average_score}%</span>
                  </li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <TrendingDown className="h-4 w-4 text-amber-600" />
              Weak topics
            </CardTitle>
          </CardHeader>
          <CardContent>
            {analytics.weak_topics.length === 0 ? (
              <p className="text-sm text-muted-foreground">No weak topics identified.</p>
            ) : (
              <ul className="space-y-2 text-sm">
                {analytics.weak_topics.map((topic) => (
                  <li key={topic.category} className="flex justify-between">
                    <span>{topic.category}</span>
                    <span className="font-medium">{topic.average_score}%</span>
                  </li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
