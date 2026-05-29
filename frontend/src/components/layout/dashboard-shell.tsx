"use client";

import { useState, type ReactNode } from "react";

import { DashboardHeader } from "@/components/layout/dashboard-header";
import { DashboardSidebar } from "@/components/layout/dashboard-sidebar";
import { LoadingSpinner } from "@/components/common/loading-spinner";
import { useAuth } from "@/hooks/use-auth";
import { cn } from "@/lib/utils";

interface DashboardShellProps {
  children: ReactNode;
  title: string;
  description?: string;
}

export function DashboardShell({ children, title, description }: DashboardShellProps) {
  const { isLoading } = useAuth();
  const [mobileNavOpen, setMobileNavOpen] = useState(false);

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <LoadingSpinner label="Loading dashboard" />
      </div>
    );
  }

  return (
    <div className="flex min-h-screen bg-muted/30">
      <DashboardSidebar className="hidden lg:flex" />

      {mobileNavOpen && (
        <div className="fixed inset-0 z-40 lg:hidden">
          <button
            type="button"
            className="absolute inset-0 bg-black/50"
            aria-label="Close navigation"
            onClick={() => setMobileNavOpen(false)}
          />
          <DashboardSidebar
            className="relative z-50 shadow-lg"
            onNavigate={() => setMobileNavOpen(false)}
          />
        </div>
      )}

      <div className="flex min-w-0 flex-1 flex-col">
        <DashboardHeader
          title={title}
          description={description}
          onMenuClick={() => setMobileNavOpen(true)}
        />
        <main className={cn("flex-1 p-4 sm:p-6")}>{children}</main>
      </div>
    </div>
  );
}
