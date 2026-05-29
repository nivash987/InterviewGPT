"use client";

import Link from "next/link";

import { DashboardShell } from "@/components/layout/dashboard-shell";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ROUTES } from "@/constants/routes";
import { useAuth } from "@/hooks/use-auth";

export default function DashboardPage() {
  const { user } = useAuth();

  return (
    <DashboardShell
      title="Dashboard"
      description="Your preparation hub. More modules will appear here as they ship."
    >
      <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle>Welcome{user?.full_name ? `, ${user.full_name.split(" ")[0]}` : ""}</CardTitle>
            <CardDescription>
              You are signed in as {user?.email ?? "…"}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              Email verified: {user?.is_email_verified ? "Yes" : "Pending verification"}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Mock interviews</CardTitle>
            <CardDescription>Coming soon</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              Start AI mock sessions from this dashboard once the interview module is connected.
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Resumes</CardTitle>
            <CardDescription>Upload and manage your CV</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground mb-4">
              Upload PDF or DOCX resumes with automatic parsing for skills, experience, and education.
            </p>
            <Link
              href={ROUTES.resumes}
              className="inline-flex items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90"
            >
              Manage resumes
            </Link>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>ATS Analysis</CardTitle>
            <CardDescription>Score and optimize your resume</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground mb-4">
              Run rule-based ATS scoring, skill gap analysis, and role recommendations on uploaded resumes.
            </p>
            <Link
              href={ROUTES.ats}
              className="inline-flex items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90"
            >
              Open ATS dashboard
            </Link>
          </CardContent>
        </Card>
      </div>
    </DashboardShell>
  );
}
