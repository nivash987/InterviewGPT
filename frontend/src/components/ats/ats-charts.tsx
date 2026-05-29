"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import type { AtsHistoryItem, KeywordCoverage } from "@/types/ats";

interface AtsChartsProps {
  history: AtsHistoryItem[];
  keywordCoverage: KeywordCoverage | null;
}

function SimpleBarChart({
  data,
  labelKey,
  valueKey,
  maxValue = 100,
}: {
  data: Record<string, string | number>[];
  labelKey: string;
  valueKey: string;
  maxValue?: number;
}) {
  if (data.length === 0) {
    return <p className="text-sm text-muted-foreground">Not enough data to display chart.</p>;
  }

  return (
    <div className="flex h-48 items-end gap-2 sm:gap-3">
      {data.map((item, index) => {
        const value = Number(item[valueKey]);
        const height = Math.max(4, (value / maxValue) * 100);
        return (
          <div key={index} className="flex flex-1 flex-col items-center gap-1">
            <span className="text-xs font-medium tabular-nums">{value}</span>
            <div className="relative w-full flex-1">
              <div
                className="absolute bottom-0 w-full rounded-t bg-primary transition-all"
                style={{ height: `${height}%` }}
              />
            </div>
            <span className="max-w-full truncate text-[10px] text-muted-foreground sm:text-xs">
              {String(item[labelKey])}
            </span>
          </div>
        );
      })}
    </div>
  );
}

function CoverageDonut({ coverage }: { coverage: KeywordCoverage }) {
  const percent = coverage.coverage_percent;
  const circumference = 2 * Math.PI * 40;
  const offset = circumference - (percent / 100) * circumference;

  return (
    <div className="flex flex-col items-center gap-2 sm:flex-row sm:gap-6">
      <svg viewBox="0 0 100 100" className="h-32 w-32 shrink-0">
        <circle cx="50" cy="50" r="40" fill="none" stroke="currentColor" strokeWidth="8" className="text-secondary" />
        <circle
          cx="50"
          cy="50"
          r="40"
          fill="none"
          stroke="currentColor"
          strokeWidth="8"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          transform="rotate(-90 50 50)"
          className="text-primary"
        />
        <text x="50" y="50" textAnchor="middle" dominantBaseline="central" className="fill-foreground text-lg font-bold">
          {percent}%
        </text>
      </svg>
      <div className="text-sm text-muted-foreground">
        <p>
          <span className="font-medium text-foreground">{coverage.matched_keywords}</span> of{" "}
          <span className="font-medium text-foreground">{coverage.total_keywords}</span> taxonomy keywords matched
        </p>
      </div>
    </div>
  );
}

export function AtsCharts({ history, keywordCoverage }: AtsChartsProps) {
  const trendData = [...history]
    .reverse()
    .slice(-8)
    .map((item, index) => ({
      label: `#${index + 1}`,
      score: item.ats_score,
    }));

  return (
    <div className="grid gap-6 md:grid-cols-2">
      <Card>
        <CardHeader>
          <CardTitle>ATS Score Trend</CardTitle>
          <CardDescription>Recent analysis scores over time</CardDescription>
        </CardHeader>
        <CardContent>
          <SimpleBarChart
            data={trendData.map((d) => ({ label: d.label, score: d.score }))}
            labelKey="label"
            valueKey="score"
          />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Skills Coverage</CardTitle>
          <CardDescription>Keyword match against industry skill taxonomy</CardDescription>
        </CardHeader>
        <CardContent>
          {keywordCoverage ? (
            <CoverageDonut coverage={keywordCoverage} />
          ) : (
            <p className="text-sm text-muted-foreground">Run an analysis to see skills coverage.</p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
