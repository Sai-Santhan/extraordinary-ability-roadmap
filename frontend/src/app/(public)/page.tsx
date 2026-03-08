import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Shield, Upload, BarChart3, Compass, FileDown, Lock } from "lucide-react";

const features = [
  {
    icon: Upload,
    title: "Aggregate Your Data",
    description: "Import from CV, Google Scholar, GitHub, Google Takeout, ChatGPT exports, and LinkedIn — all in one place.",
  },
  {
    icon: BarChart3,
    title: "AI-Powered Assessment",
    description: "Claude AI scores your evidence against EB-1A, NIW, or O-1 criteria with calibrated confidence levels.",
  },
  {
    icon: Compass,
    title: "Personalized Roadmap",
    description: "Get a time-phased action plan with specific conferences, journals, and opportunities to strengthen your case.",
  },
  {
    icon: Shield,
    title: "Criteria Dashboard",
    description: "Interactive radar chart maps your evidence to all 10 USCIS criteria. See strengths, gaps, and next steps.",
  },
  {
    icon: FileDown,
    title: "Export Anywhere",
    description: "Download your profile as JSON, Markdown, PDF, or DOCX. Your data is yours — portable and open.",
  },
  {
    icon: Lock,
    title: "Privacy First",
    description: "Explicit consent before processing. Full transparency on what's sent to AI. One-click data deletion.",
  },
];

export default function LandingPage() {
  return (
    <div className="flex flex-col min-h-screen">
      {/* Skip link */}
      <a
        href="#hero"
        className="sr-only focus:not-sr-only focus:absolute focus:z-50 focus:top-2 focus:left-2 focus:rounded-md focus:bg-primary focus:px-4 focus:py-2 focus:text-primary-foreground focus:text-sm"
      >
        Skip to main content
      </a>

      {/* Nav */}
      <nav aria-label="Main navigation" className="flex items-center justify-between px-4 sm:px-6 py-4 max-w-7xl mx-auto w-full">
        <div className="flex items-center gap-2.5">
          <div className="h-9 w-9 rounded-xl bg-primary flex items-center justify-center" aria-hidden="true">
            <Compass className="h-5 w-5 text-primary-foreground" />
          </div>
          <span className="text-lg sm:text-xl font-semibold tracking-tight">EB1A Immigration Roadmap</span>
        </div>
        <div className="flex items-center gap-2 sm:gap-3">
          <Link href="/login">
            <Button variant="ghost" size="sm" className="sm:size-default">Log in</Button>
          </Link>
          <Link href="/register">
            <Button size="sm" className="sm:size-default">Get Started</Button>
          </Link>
        </div>
      </nav>

      {/* Hero */}
      <section id="hero" aria-label="Introduction" className="flex flex-col items-center text-center px-4 sm:px-6 pt-12 sm:pt-20 pb-12 sm:pb-16 max-w-4xl mx-auto">
        <div className="inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/5 px-4 py-1.5 text-sm text-primary mb-6">
          <Shield className="h-3.5 w-3.5" />
          Data Portability Hackathon — Track 3
        </div>
        <h1 className="text-3xl sm:text-5xl lg:text-6xl font-bold tracking-tight">
          Turn Your Career Data Into an{" "}
          <span className="text-primary">Immigration Roadmap</span>
        </h1>
        <p className="mt-4 sm:mt-6 text-base sm:text-lg text-muted-foreground max-w-2xl leading-relaxed">
          Aggregate your scattered career achievements, score them against USCIS
          criteria with AI, and get a personalized plan to qualify for EB-1A,
          NIW, or O-1 — faster.
        </p>
        <div className="mt-6 sm:mt-8 flex flex-col sm:flex-row gap-3 w-full sm:w-auto">
          <Link href="/register" className="w-full sm:w-auto">
            <Button size="lg" className="text-base w-full sm:w-auto sm:px-8">
              Start Free Analysis
            </Button>
          </Link>
          <Link href="/login" className="w-full sm:w-auto">
            <Button size="lg" variant="outline" className="text-base w-full sm:w-auto sm:px-8">
              Log In
            </Button>
          </Link>
        </div>
        <p className="mt-4 text-xs text-muted-foreground/60">
          This tool is not legal advice. Consult a qualified immigration attorney.
        </p>
      </section>

      {/* Features */}
      <section aria-label="Features" className="px-4 sm:px-6 py-12 sm:py-16 max-w-7xl mx-auto w-full">
        <h2 className="text-2xl sm:text-3xl font-bold text-center mb-8 sm:mb-12">
          How It Works
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
          {features.map((feature) => (
            <Card key={feature.title} className="group hover:shadow-md transition-shadow">
              <CardContent className="pt-6">
                <div className="h-10 w-10 rounded-xl bg-primary/10 flex items-center justify-center mb-4 group-hover:bg-primary/15 transition-colors">
                  <feature.icon className="h-5 w-5 text-primary" />
                </div>
                <h3 className="font-semibold text-base sm:text-lg mb-1.5">{feature.title}</h3>
                <p className="text-muted-foreground text-sm leading-relaxed">{feature.description}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer className="mt-auto border-t px-4 sm:px-6 py-6 sm:py-8 text-center text-sm text-muted-foreground">
        <p>Built for the Data Portability Hackathon | Track 3: Personal Data, Personal Value</p>
        <p className="mt-1 text-xs">This tool is not legal advice and does not replace an immigration attorney.</p>
      </footer>
    </div>
  );
}
