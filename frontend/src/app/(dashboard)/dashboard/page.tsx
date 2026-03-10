"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Upload, BarChart3, Route, FileDown, ArrowRight, AlertCircle } from "lucide-react";
import { apiClient } from "@/lib/api";
import { useAuthStore } from "@/lib/store";
import { toast } from "sonner";

const PATHWAY_NAMES: Record<string, string> = {
  eb1a: "EB-1A",
  eb1b: "EB-1B",
  eb1c: "EB-1C",
  niw: "NIW",
  o1: "O-1",
};

interface Profile {
  id: string;
  status: string;
  target_pathway: string | null;
  pathway_changed_since_analysis: boolean;
  last_analysis_run: string | null;
  profile_data: Record<string, unknown> | null;
  assessment_data: Record<string, unknown> | null;
  roadmap_data: Record<string, unknown> | null;
  created_at: string;
}

export default function DashboardPage() {
  const [profiles, setProfiles] = useState<Profile[]>([]);
  const [loading, setLoading] = useState(true);
  const userName = useAuthStore((s) => s.userName);

  useEffect(() => {
    apiClient
      .get<Profile[]>("/api/profiles/")
      .then(setProfiles)
      .catch(() => toast.error("Failed to load profile data"))
      .finally(() => setLoading(false));
  }, []);

  const latestProfile = profiles[0];
  const status = latestProfile?.status || "none";
  const criteriaMetCount = (latestProfile?.assessment_data as Record<string, unknown>)?.criteria_met_count as number | undefined;
  const pathway = latestProfile?.target_pathway;
  const pathwayChanged = latestProfile?.pathway_changed_since_analysis;

  const statusBadge = {
    none: { label: "No profile", variant: "secondary" as const },
    created: { label: "Ready to upload", variant: "secondary" as const },
    ingesting: { label: "Processing files...", variant: "default" as const },
    extracting: { label: "Extracting profile...", variant: "default" as const },
    assessing: { label: "Assessing criteria...", variant: "default" as const },
    roadmapping: { label: "Generating roadmap...", variant: "default" as const },
    complete: { label: "Analysis complete", variant: "default" as const },
  }[status] || { label: status, variant: "secondary" as const };

  const quickActions = [
    { title: "Upload Evidence", description: "Add your CV, publications, and career data", href: "/dashboard/evidence", icon: Upload },
    { title: "View Criteria", description: "See how your evidence maps to USCIS criteria", href: "/dashboard/criteria", icon: BarChart3 },
    { title: "View Roadmap", description: "Your personalized immigration action plan", href: "/dashboard/roadmap", icon: Route },
    { title: "Export Profile", description: "Download as JSON, PDF, Markdown, or DOCX", href: "/dashboard/export", icon: FileDown },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold">Welcome back{userName ? `, ${userName.split(" ")[0]}` : ""}</h1>
        <p className="text-muted-foreground mt-1">
          Here&apos;s an overview of your immigration profile
        </p>
      </div>

      {/* Pathway changed banner */}
      {pathwayChanged && (
        <div className="flex items-center gap-3 rounded-lg border border-amber-200 dark:border-amber-800 bg-amber-50 dark:bg-amber-950/20 p-4">
          <AlertCircle className="h-5 w-5 text-amber-600 shrink-0" />
          <div className="flex-1">
            <p className="text-sm font-medium">Pathway changed to {PATHWAY_NAMES[pathway || ""] || pathway}</p>
            <p className="text-xs text-muted-foreground">Re-run analysis from the Evidence page to update your criteria assessment and roadmap.</p>
          </div>
          <Link href="/dashboard/evidence">
            <Button size="sm" variant="outline">Re-run Analysis</Button>
          </Link>
        </div>
      )}

      {/* Status Card */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Profile Status</CardTitle>
              <CardDescription>
                {latestProfile
                  ? `Created ${new Date(latestProfile.created_at).toLocaleDateString()}`
                  : "Create a profile to get started"}
              </CardDescription>
            </div>
            <div className="flex items-center gap-2">
              {pathway && (
                <Badge variant="outline">{PATHWAY_NAMES[pathway] || pathway.toUpperCase()}</Badge>
              )}
              <Badge variant={statusBadge.variant}>{statusBadge.label}</Badge>
            </div>
          </div>
        </CardHeader>
        {status === "complete" && criteriaMetCount !== undefined && (
          <CardContent>
            <div className="grid grid-cols-3 gap-4 text-center">
              <div>
                <p className="text-2xl font-bold text-green-600">{criteriaMetCount}</p>
                <p className="text-sm text-muted-foreground">Criteria Met</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-amber-600">
                  {(latestProfile?.assessment_data as Record<string, unknown>)?.criteria_close_count as number || 0}
                </p>
                <p className="text-sm text-muted-foreground">Close</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-primary">
                  {String((latestProfile?.assessment_data as Record<string, unknown>)?.overall_readiness || "—")}
                </p>
                <p className="text-sm text-muted-foreground">Readiness</p>
              </div>
            </div>
          </CardContent>
        )}
      </Card>

      {/* Quick Actions */}
      <nav aria-label="Quick actions" className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {quickActions.map((action) => (
          <Link key={action.href} href={action.href}>
            <Card className="hover:bg-accent/50 transition-colors cursor-pointer h-full">
              <CardContent className="flex items-center gap-4 pt-6">
                <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center shrink-0">
                  <action.icon className="h-5 w-5 text-primary" />
                </div>
                <div className="flex-1">
                  <h3 className="font-medium">{action.title}</h3>
                  <p className="text-sm text-muted-foreground">{action.description}</p>
                </div>
                <ArrowRight className="h-4 w-4 text-muted-foreground" aria-hidden="true" />
              </CardContent>
            </Card>
          </Link>
        ))}
      </nav>

      {/* Disclaimer */}
      <p className="text-xs text-muted-foreground text-center">
        This tool is not legal advice and does not replace an immigration attorney.
      </p>
    </div>
  );
}
