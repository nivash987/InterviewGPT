import Link from "next/link";

import { ROUTES } from "@/constants/routes";
import { cn } from "@/lib/utils";

interface LogoProps {
  className?: string;
  showText?: boolean;
}

export function Logo({ className, showText = true }: LogoProps) {
  return (
    <Link href={ROUTES.home} className={cn("inline-flex items-center gap-2 font-semibold", className)}>
      <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary text-sm font-bold text-primary-foreground">
        IG
      </span>
      {showText && <span className="text-lg tracking-tight">InterviewGPT</span>}
    </Link>
  );
}
