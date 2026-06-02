"use client";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import type { InterviewHistoryItem } from "@/types/interview";

interface InterviewHistoryTableProps {
  items: InterviewHistoryItem[];
  loading?: boolean;
  onView: (sessionId: string) => void;
}

export function InterviewHistoryTable({
  items,
  loading = false,
  onView,
}: InterviewHistoryTableProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Interview history</CardTitle>
        <CardDescription>Past mock interview sessions</CardDescription>
      </CardHeader>
      <CardContent>
        {loading ? (
          <p className="text-sm text-muted-foreground">Loading history...</p>
        ) : items.length === 0 ? (
          <p className="text-sm text-muted-foreground">No interviews yet. Start your first mock interview.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-left text-muted-foreground">
                  <th className="pb-2 pr-4 font-medium">Role</th>
                  <th className="pb-2 pr-4 font-medium">Resume</th>
                  <th className="pb-2 pr-4 font-medium">Difficulty</th>
                  <th className="pb-2 pr-4 font-medium">Score</th>
                  <th className="pb-2 pr-4 font-medium">Status</th>
                  <th className="pb-2 font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {items.map((item) => (
                  <tr key={item.id} className="border-b last:border-0">
                    <td className="py-3 pr-4">{item.role}</td>
                    <td className="py-3 pr-4">{item.resume_title ?? "—"}</td>
                    <td className="py-3 pr-4 capitalize">{item.difficulty}</td>
                    <td className="py-3 pr-4">
                      {item.total_score !== null ? `${item.total_score}%` : "—"}
                    </td>
                    <td className="py-3 pr-4 capitalize">{item.status.replace("_", " ")}</td>
                    <td className="py-3">
                      <Button variant="outline" size="sm" onClick={() => onView(item.id)}>
                        View
                      </Button>
                    </td>
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
