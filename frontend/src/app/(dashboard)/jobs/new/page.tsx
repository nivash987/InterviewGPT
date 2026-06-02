"use client";

import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { DashboardShell } from "@/components/layout/dashboard-shell";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ROUTES } from "@/constants/routes";
import { useAuth } from "@/hooks/use-auth";
import { jobsService } from "@/services/api/jobs.service";
import { APPLICATION_STATUSES, type ApplicationStatus } from "@/types/jobs";

export default function NewJobApplicationPage() {
  const router = useRouter();
  const { isAuthenticated } = useAuth();
  const [companyName, setCompanyName] = useState("");
  const [roleTitle, setRoleTitle] = useState("");
  const [status, setStatus] = useState<ApplicationStatus>("applied");
  const [location, setLocation] = useState("");
  const [jobUrl, setJobUrl] = useState("");
  const [salaryRange, setSalaryRange] = useState("");
  const [description, setDescription] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!isAuthenticated) {
      router.replace(ROUTES.login);
    }
  }, [isAuthenticated, router]);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      const created = await jobsService.create({
        company_name: companyName.trim(),
        role_title: roleTitle.trim(),
        status,
        location: location.trim() || undefined,
        job_url: jobUrl.trim() || undefined,
        salary_range: salaryRange.trim() || undefined,
        description: description.trim() || undefined,
      });
      router.push(`${ROUTES.jobs}/${created.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create application");
      setSubmitting(false);
    }
  };

  return (
    <DashboardShell
      title="New Application"
      description="Add a job application to your tracker."
    >
      <Card className="mx-auto max-w-lg">
        <CardHeader>
          <CardTitle>Application details</CardTitle>
          <CardDescription>Company, role, and initial status.</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <p className="rounded-md border border-destructive/50 bg-destructive/10 px-4 py-2 text-sm text-destructive">
                {error}
              </p>
            )}
            <div className="space-y-2">
              <Label htmlFor="company">Company</Label>
              <Input
                id="company"
                value={companyName}
                onChange={(e) => setCompanyName(e.target.value)}
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="role">Role title</Label>
              <Input
                id="role"
                value={roleTitle}
                onChange={(e) => setRoleTitle(e.target.value)}
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="status">Status</Label>
              <select
                id="status"
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                value={status}
                onChange={(e) => setStatus(e.target.value as ApplicationStatus)}
              >
                {APPLICATION_STATUSES.map((s) => (
                  <option key={s} value={s}>
                    {s.replace(/_/g, " ")}
                  </option>
                ))}
              </select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="location">Location</Label>
              <Input id="location" value={location} onChange={(e) => setLocation(e.target.value)} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="jobUrl">Job URL</Label>
              <Input id="jobUrl" type="url" value={jobUrl} onChange={(e) => setJobUrl(e.target.value)} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="salary">Salary range</Label>
              <Input
                id="salary"
                value={salaryRange}
                onChange={(e) => setSalaryRange(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="description">Description</Label>
              <textarea
                id="description"
                className="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
              />
            </div>
            <div className="flex gap-2">
              <Button type="submit" disabled={submitting}>
                {submitting ? "Saving…" : "Create application"}
              </Button>
              <Button type="button" variant="outline" onClick={() => router.push(ROUTES.jobs)}>
                Cancel
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </DashboardShell>
  );
}
