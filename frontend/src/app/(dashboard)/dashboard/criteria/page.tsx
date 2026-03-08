"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { CriteriaRadarChart } from "@/components/criteria-radar-chart";
import { CriterionCard } from "@/components/criterion-card";
import { apiClient } from "@/lib/api";

interface CriterionScore {
  criterion_number: number;
  criterion_name: string;
  evidence_found: string[];
  strength: string;
  confidence: { data_confidence: number; criteria_match: number; overall: number; reasoning: string };
  gaps: string[];
  priority_actions: string[];
}

interface Assessment {
  pathway: string;
  criteria_scores: CriterionScore[];
  criteria_met_count: number;
  criteria_close_count: number;
  overall_readiness: string;
  strongest_criteria: number[];
  weakest_criteria: number[];
  recommended_focus: number[];
}

interface Profile {
  id: string;
  status: string;
  assessment_data: Assessment | null;
}

export default function CriteriaPage() {
  const [assessment, setAssessment] = useState<Assessment | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const profiles = await apiClient.get<Profile[]>("/api/profiles/");
        if (profiles.length > 0 && profiles[0].assessment_data) {
          setAssessment(profiles[0].assessment_data);
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
    return <div className="flex items-center justify-center h-64 text-muted-foreground">Loading...</div>;
  }

  if (!assessment) {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-center">
        <p className="text-muted-foreground">No assessment data yet.</p>
        <p className="text-sm text-muted-foreground mt-1">Upload evidence and run the analysis first.</p>
      </div>
    );
  }

  const radarData = assessment.criteria_scores.map((cs) => ({
    criterion: cs.criterion_name.split(" ").slice(0, 2).join(" "),
    score: cs.confidence.overall,
    fullMark: 100,
  }));

  const readinessColor = {
    "ready to file": "bg-green-100 text-green-800",
    "1-2 years": "bg-primary/10 text-primary",
    "2-4 years": "bg-amber-100 text-amber-800",
    "significant gaps": "bg-red-100 text-red-800",
  }[assessment.overall_readiness] || "bg-muted text-muted-foreground";

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold">Criteria Assessment</h1>
        <p className="text-muted-foreground mt-1">
          Your evidence scored against {assessment.pathway.toUpperCase()} criteria
        </p>
      </div>

      {/* Summary */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4" role="list" aria-label="Assessment summary">
        <Card>
          <CardContent className="pt-6 text-center">
            <p className="text-3xl font-bold text-green-600">{assessment.criteria_met_count}</p>
            <p className="text-sm text-muted-foreground">Criteria Met</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6 text-center">
            <p className="text-3xl font-bold text-amber-600">{assessment.criteria_close_count}</p>
            <p className="text-sm text-muted-foreground">Close to Meeting</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6 text-center">
            <Badge className={`text-sm px-3 py-1 ${readinessColor}`}>{assessment.overall_readiness}</Badge>
            <p className="text-sm text-muted-foreground mt-2">Overall Readiness</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6 text-center">
            <p className="text-3xl font-bold text-primary">{assessment.recommended_focus.length}</p>
            <p className="text-sm text-muted-foreground">Focus Areas</p>
          </CardContent>
        </Card>
      </div>

      {/* Radar Chart */}
      <Card>
        <CardHeader>
          <CardTitle>Criteria Radar</CardTitle>
          <CardDescription>Overall confidence scores across all {assessment.pathway.toUpperCase()} criteria</CardDescription>
        </CardHeader>
        <CardContent>
          <CriteriaRadarChart data={radarData} />
        </CardContent>
      </Card>

      {/* Individual Criteria Cards */}
      <div>
        <h2 className="text-xl font-semibold mb-4">Detailed Criteria Breakdown</h2>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {assessment.criteria_scores.map((cs) => (
            <CriterionCard key={cs.criterion_number} criterion={cs} />
          ))}
        </div>
      </div>

      <p className="text-xs text-muted-foreground text-center">
        AI assessments include confidence scores indicating uncertainty. Verify all findings with qualified counsel.
      </p>
    </div>
  );
}
