import type { Metadata } from "next";
import Link from "next/link";

import { LoginForm } from "@/components/auth/login-form";
import { AuthLayout } from "@/components/layout/auth-layout";
import { Card, CardContent } from "@/components/ui/card";
import { ROUTES } from "@/constants/routes";

export const metadata: Metadata = {
  title: "Sign in",
};

export default function LoginPage() {
  return (
    <AuthLayout
      title="Welcome back"
      description="Sign in to continue to your InterviewGPT dashboard."
      footer={
        <p className="text-center text-sm text-muted-foreground">
          Don&apos;t have an account?{" "}
          <Link href={ROUTES.register} className="font-medium text-primary hover:underline">
            Create one
          </Link>
        </p>
      }
    >
      <Card>
        <CardContent className="pt-6">
          <LoginForm />
        </CardContent>
      </Card>
    </AuthLayout>
  );
}
