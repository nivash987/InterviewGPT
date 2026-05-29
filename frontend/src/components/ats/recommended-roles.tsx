"use client";

import { Briefcase } from "lucide-react";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import type { RecommendedRole } from "@/types/ats";

interface RecommendedRolesPanelProps {
  roles: RecommendedRole[];
}

export function RecommendedRolesPanel({ roles }: RecommendedRolesPanelProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Briefcase className="h-5 w-5" />
          Recommended Roles
        </CardTitle>
        <CardDescription>Roles that best match your current skill profile</CardDescription>
      </CardHeader>
      <CardContent>
        {roles.length === 0 ? (
          <p className="text-sm text-muted-foreground">
            Upload a resume with more skills to get role recommendations.
          </p>
        ) : (
          <div className="space-y-4">
            {roles.map((role) => (
              <div key={role.role_name} className="rounded-lg border p-4">
                <div className="flex items-center justify-between gap-4">
                  <h4 className="font-medium">{role.role_name}</h4>
                  <span className="text-sm font-semibold tabular-nums">{role.match_score}% match</span>
                </div>
                <Progress value={role.match_score} className="mt-2 h-2" />
                {role.matched_required.length > 0 && (
                  <p className="mt-2 text-xs text-muted-foreground">
                    Required matched: {role.matched_required.join(", ")}
                  </p>
                )}
                {role.missing_required.length > 0 && (
                  <p className="mt-1 text-xs text-destructive">
                    Missing required: {role.missing_required.join(", ")}
                  </p>
                )}
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
