"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useEffect, useState } from "react";

import { AuthLayout } from "@/components/layout/auth-layout";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { ROUTES } from "@/constants/routes";
import { getErrorMessage } from "@/lib/errors";
import { authService } from "@/services";

function VerifyEmailContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const tokenFromUrl = searchParams.get("token");
  const emailFromUrl = searchParams.get("email");

  const [status, setStatus] = useState<"idle" | "loading" | "success" | "error">("idle");
  const [message, setMessage] = useState<string | null>(null);
  const [resendEmail, setResendEmail] = useState(emailFromUrl ?? "");
  const [isResending, setIsResending] = useState(false);

  useEffect(() => {
    if (!tokenFromUrl) {
      return;
    }

    let cancelled = false;

    async function verify() {
      setStatus("loading");
      try {
        const result = await authService.verifyEmail(tokenFromUrl!);
        if (!cancelled) {
          setStatus("success");
          setMessage(result.message);
        }
      } catch (err) {
        if (!cancelled) {
          setStatus("error");
          setMessage(getErrorMessage(err, "Unable to verify email"));
        }
      }
    }

    void verify();
    return () => {
      cancelled = true;
    };
  }, [tokenFromUrl]);

  async function handleResend(event: React.FormEvent) {
    event.preventDefault();
    if (!resendEmail.trim()) {
      return;
    }

    setIsResending(true);
    setMessage(null);
    try {
      const result = await authService.resendVerification(resendEmail.trim());
      setMessage(result.message);
    } catch (err) {
      setMessage(getErrorMessage(err, "Unable to resend verification email"));
    } finally {
      setIsResending(false);
    }
  }

  return (
    <AuthLayout
      title="Verify your email"
      description="Confirm your email address to access your InterviewGPT account."
      footer={
        <p className="text-center text-sm text-muted-foreground">
          Already verified?{" "}
          <Link href={ROUTES.login} className="font-medium text-primary hover:underline">
            Sign in
          </Link>
        </p>
      }
    >
      <Card>
        <CardContent className="space-y-4 pt-6">
          {!tokenFromUrl && (
            <p className="text-sm text-muted-foreground">
              Open the verification link from your email, or request a new one below.
            </p>
          )}

          {status === "loading" && (
            <p className="text-sm text-muted-foreground">Verifying your email address…</p>
          )}

          {status === "success" && (
            <div className="space-y-3">
              <p className="text-sm text-green-700">{message}</p>
              <Button className="w-full" onClick={() => router.push(ROUTES.login)}>
                Continue to sign in
              </Button>
            </div>
          )}

          {status === "error" && (
            <div
              role="alert"
              className="rounded-md border border-destructive/50 bg-destructive/10 px-3 py-2 text-sm text-destructive"
            >
              {message}
            </div>
          )}

          {(status === "idle" || status === "error") && (
            <form onSubmit={handleResend} className="space-y-3">
              <p className="text-sm font-medium">Resend verification email</p>
              <Input
                type="email"
                autoComplete="email"
                placeholder="you@example.com"
                value={resendEmail}
                onChange={(event) => setResendEmail(event.target.value)}
              />
              <Button type="submit" variant="outline" className="w-full" disabled={isResending}>
                {isResending ? "Sending…" : "Resend email"}
              </Button>
            </form>
          )}

          {message && status !== "success" && status !== "error" && (
            <p className="text-sm text-muted-foreground">{message}</p>
          )}
        </CardContent>
      </Card>
    </AuthLayout>
  );
}

export default function VerifyEmailPage() {
  return (
    <Suspense fallback={<p className="p-6 text-sm text-muted-foreground">Loading…</p>}>
      <VerifyEmailContent />
    </Suspense>
  );
}
