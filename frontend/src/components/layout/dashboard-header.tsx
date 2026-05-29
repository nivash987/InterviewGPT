"use client";

import { Menu } from "lucide-react";

import { PageHeader } from "@/components/common/page-header";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useAuth } from "@/hooks/use-auth";

function getInitials(name: string | null | undefined, email: string): string {
  if (name?.trim()) {
    const parts = name.trim().split(/\s+/);
    if (parts.length >= 2) {
      return `${parts[0][0]}${parts[1][0]}`.toUpperCase();
    }
    return name.slice(0, 2).toUpperCase();
  }
  return email.slice(0, 2).toUpperCase();
}

interface DashboardHeaderProps {
  title: string;
  description?: string;
  onMenuClick?: () => void;
}

export function DashboardHeader({ title, description, onMenuClick }: DashboardHeaderProps) {
  const { user, logout } = useAuth();

  return (
    <div className="space-y-4 border-b bg-background px-4 py-4 sm:px-6">
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-start gap-3">
          {onMenuClick && (
            <Button
              variant="outline"
              size="icon"
              className="shrink-0 lg:hidden"
              onClick={onMenuClick}
              aria-label="Open navigation"
            >
              <Menu className="h-4 w-4" />
            </Button>
          )}
          <PageHeader title={title} description={description} className="flex-1" />
        </div>

        {user && (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="relative h-10 w-10 rounded-full">
                <Avatar>
                  <AvatarFallback>
                    {getInitials(user.full_name, user.email)}
                  </AvatarFallback>
                </Avatar>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-56">
              <DropdownMenuLabel className="font-normal">
                <div className="flex flex-col space-y-1">
                  <p className="text-sm font-medium">{user.full_name ?? "Account"}</p>
                  <p className="text-xs text-muted-foreground">{user.email}</p>
                </div>
              </DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={() => void logout()}>Sign out</DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        )}
      </div>
    </div>
  );
}
