import Link from "next/link";
import { ArrowRight, Brain, LineChart, Mic } from "lucide-react";

import { SiteHeader } from "@/components/layout/site-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ROUTES } from "@/constants/routes";

const features = [
  {
    icon: Mic,
    title: "Mock interviews",
    description:
      "Practice with AI-driven mock sessions tailored to your target role and experience level.",
  },
  {
    icon: Brain,
    title: "Personalized feedback",
    description:
      "Get structured evaluations and actionable suggestions after every answer you submit.",
  },
  {
    icon: LineChart,
    title: "Progress tracking",
    description:
      "Monitor readiness over time with dashboards built for consistent, focused preparation.",
  },
] as const;

export default function LandingPage() {
  return (
    <div className="flex min-h-screen flex-col">
      <SiteHeader />

      <main className="flex-1">
        <section className="container mx-auto px-4 py-16 md:py-24">
          <div className="mx-auto max-w-3xl text-center">
            <p className="mb-4 inline-block rounded-full bg-primary/10 px-3 py-1 text-sm font-medium text-primary">
              AI-powered interview prep
            </p>
            <h1 className="text-4xl font-bold tracking-tight sm:text-5xl md:text-6xl">
              Prepare smarter. Interview with confidence.
            </h1>
            <p className="mt-6 text-lg text-muted-foreground">
              InterviewGPT helps you practice, receive feedback, and track progress — all in one
              place built for modern hiring loops.
            </p>
            <div className="mt-8 flex flex-col items-center justify-center gap-3 sm:flex-row">
              <Button size="lg" asChild>
                <Link href={ROUTES.register}>
                  Start free
                  <ArrowRight className="ml-1 h-4 w-4" />
                </Link>
              </Button>
              <Button size="lg" variant="outline" asChild>
                <Link href={ROUTES.login}>Sign in</Link>
              </Button>
            </div>
          </div>
        </section>

        <section id="features" className="border-t bg-muted/30 py-16 md:py-20">
          <div className="container mx-auto px-4">
            <div className="mx-auto mb-12 max-w-2xl text-center">
              <h2 className="text-3xl font-bold tracking-tight">Built for serious practice</h2>
              <p className="mt-3 text-muted-foreground">
                A scalable foundation for authentication, dashboards, and future interview modules.
              </p>
            </div>
            <div className="grid gap-6 md:grid-cols-3">
              {features.map((feature) => {
                const Icon = feature.icon;
                return (
                  <Card key={feature.title}>
                    <CardHeader>
                      <div className="mb-2 flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 text-primary">
                        <Icon className="h-5 w-5" />
                      </div>
                      <CardTitle>{feature.title}</CardTitle>
                      <CardDescription>{feature.description}</CardDescription>
                    </CardHeader>
                    <CardContent />
                  </Card>
                );
              })}
            </div>
          </div>
        </section>

        <section id="how-it-works" className="container mx-auto px-4 py-16 md:py-20">
          <div className="mx-auto max-w-2xl rounded-xl border bg-card p-8 text-center shadow-sm">
            <h2 className="text-2xl font-bold">Ready when you are</h2>
            <p className="mt-3 text-muted-foreground">
              Create an account, sign in, and open your dashboard. Resume upload and ATS analysis
              will plug in here next.
            </p>
            <Button className="mt-6" asChild>
              <Link href={ROUTES.register}>Create your account</Link>
            </Button>
          </div>
        </section>
      </main>

      <footer className="border-t py-8 text-center text-sm text-muted-foreground">
        <p>© {new Date().getFullYear()} InterviewGPT. All rights reserved.</p>
      </footer>
    </div>
  );
}
