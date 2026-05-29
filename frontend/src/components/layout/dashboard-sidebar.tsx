"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutDashboard, LogOut } from "lucide-react";

import { Logo } from "@/components/common/logo";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { ROUTES } from "@/constants/routes";
import { useAuth } from "@/hooks/use-auth";
import { cn } from "@/lib/utils";

const navItems = [
  {
    href: ROUTES.dashboard,
    label: "Overview",
    icon: LayoutDashboard,
  },
] as const;

interface DashboardSidebarProps {
  onNavigate?: () => void;
  className?: string;
}

export function DashboardSidebar({ onNavigate, className }: DashboardSidebarProps) {
  const pathname = usePathname();
  const { user, logout } = useAuth();

  return (
    <aside
      className={cn(
        "flex h-full w-64 flex-col border-r bg-card",
        className,
      )}
    >
      <div className="flex h-16 items-center border-b px-4">
        <Logo showText />
      </div>

      <nav className="flex-1 space-y-1 p-4">
        {navItems.map((item) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;
          return (
            <Link
              key={item.href}
              href={item.href}
              onClick={onNavigate}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                isActive
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:bg-accent hover:text-accent-foreground",
              )}
            >
              <Icon className="h-4 w-4" />
              {item.label}
            </Link>
          );
        })}
      </nav>

      <div className="mt-auto border-t p-4">
        {user && (
          <div className="mb-3 truncate text-sm">
            <p className="font-medium">{user.full_name ?? "User"}</p>
            <p className="truncate text-muted-foreground">{user.email}</p>
          </div>
        )}
        <Separator className="mb-3" />
        <Button
          variant="outline"
          className="w-full justify-start gap-2"
          onClick={() => void logout()}
        >
          <LogOut className="h-4 w-4" />
          Sign out
        </Button>
      </div>
    </aside>
  );
}
