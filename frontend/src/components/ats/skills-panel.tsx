"use client";

import { CheckCircle2, XCircle } from "lucide-react";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

interface SkillsPanelProps {
  skillsFound: string[];
  missingSkills: string[];
}

function SkillBadge({ skill, variant }: { skill: string; variant: "found" | "missing" }) {
  const isFound = variant === "found";
  return (
    <span
      className={
        isFound
          ? "inline-flex items-center gap-1 rounded-full bg-green-100 px-2.5 py-0.5 text-xs font-medium text-green-800 dark:bg-green-900/30 dark:text-green-300"
          : "inline-flex items-center gap-1 rounded-full bg-red-100 px-2.5 py-0.5 text-xs font-medium text-red-800 dark:bg-red-900/30 dark:text-red-300"
      }
    >
      {isFound ? <CheckCircle2 className="h-3 w-3" /> : <XCircle className="h-3 w-3" />}
      {skill}
    </span>
  );
}

export function SkillsPanel({ skillsFound, missingSkills }: SkillsPanelProps) {
  return (
    <div className="grid gap-6 md:grid-cols-2">
      <Card>
        <CardHeader>
          <CardTitle>Skills Found</CardTitle>
          <CardDescription>{skillsFound.length} skills detected in your resume</CardDescription>
        </CardHeader>
        <CardContent>
          {skillsFound.length === 0 ? (
            <p className="text-sm text-muted-foreground">No skills detected yet.</p>
          ) : (
            <div className="flex flex-wrap gap-2">
              {skillsFound.map((skill) => (
                <SkillBadge key={skill} skill={skill} variant="found" />
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Missing Skills</CardTitle>
          <CardDescription>Skills to consider adding for your target roles</CardDescription>
        </CardHeader>
        <CardContent>
          {missingSkills.length === 0 ? (
            <p className="text-sm text-muted-foreground">No critical skill gaps identified.</p>
          ) : (
            <div className="flex flex-wrap gap-2">
              {missingSkills.map((skill) => (
                <SkillBadge key={skill} skill={skill} variant="missing" />
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
