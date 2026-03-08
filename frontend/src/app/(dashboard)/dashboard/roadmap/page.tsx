"use client";

import { useEffect, useState } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Target, Zap, Clock, TrendingUp } from "lucide-react";
import { apiClient } from "@/lib/api";

interface RoadmapAction {
  action: string;
  description: string;
  target_criterion: number[];
  quarter: string;
  effort_level: string;
  impact_level: string;
  specific_opportunities: string[];
}

interface QuarterlyMilestone {
  quarter: string;
  actions: RoadmapAction[];
  expected_criteria_improvement: Record<string, string>;
}

interface Roadmap {
  profile_id: string;
  pathway: string;
  timeline_years: number;
  milestones: QuarterlyMilestone[];
  narrative_summary: string;
  disclaimer: string;
}

interface Profile {
  id: string;
  roadmap_data: Roadmap | null;
}

const effortColors: Record<string, string> = {
  low: "bg-green-100 text-green-800",
  medium: "bg-amber-100 text-amber-800",
  high: "bg-red-100 text-red-800",
};

const impactColors: Record<string, string> = {
  low: "bg-muted text-muted-foreground",
  medium: "bg-primary/10 text-primary",
  high: "bg-purple-100 text-purple-800",
};

export default function RoadmapPage() {
  const [roadmap, setRoadmap] = useState<Roadmap | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const profiles = await apiClient.get<Profile[]>("/api/profiles/");
        if (profiles.length > 0 && profiles[0].roadmap_data) {
          setRoadmap(profiles[0].roadmap_data);
        }
      } catch {
        // Handle error
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64 text-muted-foreground">
        Loading...
      </div>
    );
  }

  if (!roadmap) {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-center">
        <p className="text-muted-foreground">No roadmap generated yet.</p>
        <p className="text-sm text-muted-foreground mt-1">
          Upload evidence and run the analysis first.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold">Immigration Roadmap</h1>
        <p className="text-muted-foreground mt-1">
          Your personalized {roadmap.pathway.toUpperCase()} action plan over{" "}
          {roadmap.timeline_years} year(s)
        </p>
      </div>

      {/* Timeline */}
      <div className="space-y-6">
        {roadmap.milestones.map((milestone, idx) => (
          <Card key={milestone.quarter}>
            <CardHeader>
              <div className="flex items-center gap-3">
                <div className="flex items-center justify-center h-10 w-10 rounded-full bg-primary text-primary-foreground font-bold text-sm" aria-hidden="true">
                  {idx + 1}
                </div>
                <div>
                  <CardTitle>{milestone.quarter}</CardTitle>
                  <CardDescription>
                    {milestone.actions.length} action(s) planned
                  </CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-3">
              {milestone.actions.map((action, actionIdx) => (
                <div
                  key={actionIdx}
                  className="rounded-lg border p-4 space-y-2"
                >
                  <div className="flex items-start justify-between gap-2">
                    <h4 className="font-medium text-sm">{action.action}</h4>
                    <div className="flex gap-1.5 shrink-0">
                      <Badge
                        variant="outline"
                        className={`text-xs ${effortColors[action.effort_level] || ""}`}
                      >
                        <Clock className="h-3 w-3 mr-1" />
                        {action.effort_level}
                      </Badge>
                      <Badge
                        variant="outline"
                        className={`text-xs ${impactColors[action.impact_level] || ""}`}
                      >
                        <TrendingUp className="h-3 w-3 mr-1" />
                        {action.impact_level}
                      </Badge>
                    </div>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    {action.description}
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {action.target_criterion.map((c) => (
                      <Badge key={c} variant="secondary" className="text-xs">
                        <Target className="h-3 w-3 mr-1" />
                        Criterion {c}
                      </Badge>
                    ))}
                  </div>
                  {action.specific_opportunities.length > 0 && (
                    <div className="text-xs text-muted-foreground">
                      <Zap className="h-3 w-3 inline mr-1" />
                      {action.specific_opportunities.join(", ")}
                    </div>
                  )}
                </div>
              ))}
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Narrative Summary */}
      {roadmap.narrative_summary && (
        <>
          <Separator />
          <Card>
            <CardHeader>
              <CardTitle>Strategy Summary</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="prose prose-sm max-w-none text-muted-foreground whitespace-pre-wrap">
                {roadmap.narrative_summary}
              </div>
            </CardContent>
          </Card>
        </>
      )}

      {/* Disclaimer */}
      <div className="rounded-lg bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-800 p-4 text-center" role="note">
        <p className="text-sm text-amber-800 dark:text-amber-200 font-medium">
          {roadmap.disclaimer}
        </p>
      </div>
    </div>
  );
}
