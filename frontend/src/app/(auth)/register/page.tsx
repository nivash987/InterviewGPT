import type { Metadata } from "next";
import Link from "next/link";

import { RegisterForm } from "@/components/auth/register-form";
import { AuthLayout } from "@/components/layout/auth-layout";
import { Card, CardContent } from "@/components/ui/card";
import { ROUTES } from "@/constants/routes";

export const metadata: Metadata = {
  title: "Create account",
};

export default function RegisterPage() {
  return (
    <AuthLayout
      title="Create your account"
      description="Join InterviewGPT and start preparing for your next interview."
      footer={
        <p className="text-center text-sm text-muted-foreground">
          Already have an account?{" "}
          <Link href={ROUTES.login} className="font-medium text-primary hover:underline">
            Sign in
          </Link>
        </p>
      }
    >
      <Card>
        <CardContent className="pt-6">
          <RegisterForm />
        </CardContent>
      </Card>
    </AuthLayout>
  );
}
