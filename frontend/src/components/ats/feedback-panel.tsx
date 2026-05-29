"use client";

import type { ComponentType } from "react";
import { AlertTriangle, Lightbulb, ThumbsUp } from "lucide-react";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

interface FeedbackPanelProps {
  strengths: string[];
  weaknesses: string[];
  suggestions: string[];
}

function FeedbackList({
  items,
  icon: Icon,
  emptyMessage,
}: {
  items: string[];
  icon: ComponentType<{ className?: string }>;
  emptyMessage: string;
}) {
  if (items.length === 0) {
    return <p className="text-sm text-muted-foreground">{emptyMessage}</p>;
  }
  return (
    <ul className="space-y-2">
      {items.map((item, index) => (
        <li key={index} className="flex gap-2 text-sm">
          <Icon className="mt-0.5 h-4 w-4 shrink-0 text-muted-foreground" />
          <span>{item}</span>
        </li>
      ))}
    </ul>
  );
}

export function FeedbackPanel({ strengths, weaknesses, suggestions }: FeedbackPanelProps) {
  return (
    <div className="grid gap-6 lg:grid-cols-3">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <ThumbsUp className="h-4 w-4 text-green-600" />
            Strengths
          </CardTitle>
          <CardDescription>What your resume does well</CardDescription>
        </CardHeader>
        <CardContent>
          <FeedbackList items={strengths} icon={ThumbsUp} emptyMessage="No strengths identified." />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <AlertTriangle className="h-4 w-4 text-yellow-600" />
            Weaknesses
          </CardTitle>
          <CardDescription>Areas that need improvement</CardDescription>
        </CardHeader>
        <CardContent>
          <FeedbackList items={weaknesses} icon={AlertTriangle} emptyMessage="No weaknesses identified." />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <Lightbulb className="h-4 w-4 text-primary" />
            Suggestions
          </CardTitle>
          <CardDescription>Actionable improvements</CardDescription>
        </CardHeader>
        <CardContent>
          <FeedbackList items={suggestions} icon={Lightbulb} emptyMessage="No suggestions at this time." />
        </CardContent>
      </Card>
    </div>
  );
}
