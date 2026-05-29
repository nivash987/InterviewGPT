import Link from "next/link";

import { Logo } from "@/components/common/logo";
import { ROUTES } from "@/constants/routes";

interface AuthLayoutProps {
  children: React.ReactNode;
  title: string;
  description: string;
  footer?: React.ReactNode;
}

export function AuthLayout({ children, title, description, footer }: AuthLayoutProps) {
  return (
    <div className="flex min-h-screen flex-col">
      <header className="border-b">
        <div className="container mx-auto flex h-16 items-center px-4">
          <Logo />
        </div>
      </header>

      <main className="flex flex-1 items-center justify-center px-4 py-12">
        <div className="w-full max-w-md space-y-6">
          <div className="space-y-2 text-center">
            <h1 className="text-2xl font-bold tracking-tight">{title}</h1>
            <p className="text-sm text-muted-foreground">{description}</p>
          </div>
          {children}
          {footer}
        </div>
      </main>

      <footer className="border-t py-6 text-center text-sm text-muted-foreground">
        <Link href={ROUTES.home} className="hover:text-foreground">
          Back to home
        </Link>
      </footer>
    </div>
  );
}
