"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import type { AtsHistoryItem } from "@/types/ats";

interface AnalysisHistoryTableProps {
  items: AtsHistoryItem[];
  loading: boolean;
}

function formatDate(iso: string): string {
  return new Date(iso).toLocaleString(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

export function AnalysisHistoryTable({ items, loading }: AnalysisHistoryTableProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Analysis History</CardTitle>
        <CardDescription>Past ATS analyses across your resumes</CardDescription>
      </CardHeader>
      <CardContent>
        {loading ? (
          <p className="text-sm text-muted-foreground">Loading history…</p>
        ) : items.length === 0 ? (
          <p className="text-sm text-muted-foreground">
            No analyses yet. Select a resume and click Analyze to get started.
          </p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-left text-muted-foreground">
                  <th className="pb-2 pr-4 font-medium">Resume</th>
                  <th className="pb-2 pr-4 font-medium">ATS Score</th>
                  <th className="pb-2 pr-4 font-medium">Completeness</th>
                  <th className="pb-2 font-medium">Date</th>
                </tr>
              </thead>
              <tbody>
                {items.map((item) => (
                  <tr key={item.id} className="border-b last:border-0">
                    <td className="py-3 pr-4">{item.resume_title ?? item.resume_id.slice(0, 8)}</td>
                    <td className="py-3 pr-4 font-medium tabular-nums">{item.ats_score}</td>
                    <td className="py-3 pr-4 tabular-nums">{item.completeness_score}</td>
                    <td className="py-3 text-muted-foreground">{formatDate(item.created_at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
