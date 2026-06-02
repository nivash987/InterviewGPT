import type { Metadata } from "next";
import Link from "next/link";

import { AuthLayout } from "@/components/layout/auth-layout";
import { Card, CardContent } from "@/components/ui/card";
import { ROUTES } from "@/constants/routes";

export const metadata: Metadata = {
  title: "Check your email",
};

export default async function CheckEmailPage({
  searchParams,
}: {
  searchParams: Promise<{ email?: string }>;
}) {
  const { email } = await searchParams;

  return (
    <AuthLayout
      title="Check your email"
      description="We sent a verification link to finish setting up your account."
      footer={
        <p className="text-center text-sm text-muted-foreground">
          Wrong address?{" "}
          <Link href={ROUTES.register} className="font-medium text-primary hover:underline">
            Register again
          </Link>
        </p>
      }
    >
      <Card>
        <CardContent className="space-y-4 pt-6 text-sm text-muted-foreground">
          {email ? (
            <p>
              If an account exists for <span className="font-medium text-foreground">{email}</span>,
              open the verification link we sent to that inbox.
            </p>
          ) : (
            <p>Open the verification link we sent to your inbox.</p>
          )}
          <p>
            After verifying,{" "}
            <Link href={ROUTES.login} className="font-medium text-primary hover:underline">
              sign in
            </Link>{" "}
            to continue.
          </p>
          <p>
            Didn&apos;t receive it?{" "}
            <Link href={ROUTES.verifyEmail} className="font-medium text-primary hover:underline">
              Resend verification email
            </Link>
          </p>
        </CardContent>
      </Card>
    </AuthLayout>
  );
}
