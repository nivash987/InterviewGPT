"use client";

import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";

interface AnswerEditorProps {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  submitting?: boolean;
  disabled?: boolean;
  lastScore?: number | null;
}

export function AnswerEditor({
  value,
  onChange,
  onSubmit,
  submitting = false,
  disabled = false,
  lastScore,
}: AnswerEditorProps) {
  return (
    <div className="space-y-4">
      <div className="space-y-2">
        <Label htmlFor="interview-answer">Your answer</Label>
        <textarea
          id="interview-answer"
          className="flex min-h-[160px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
          placeholder="Structure your answer with context, specific actions, and measurable results..."
          value={value}
          onChange={(e) => onChange(e.target.value)}
          disabled={disabled || submitting}
        />
        <p className="text-xs text-muted-foreground">{value.trim().length} characters</p>
      </div>
      {lastScore !== null && lastScore !== undefined && (
        <p className="text-sm text-muted-foreground">Last submitted score: {lastScore}%</p>
      )}
      <Button onClick={onSubmit} disabled={disabled || submitting || !value.trim()}>
        {submitting ? "Submitting..." : "Submit answer"}
      </Button>
    </div>
  );
}
