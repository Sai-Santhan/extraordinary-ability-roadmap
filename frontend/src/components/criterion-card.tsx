"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ConfidenceBadge } from "@/components/confidence-badge";
import { ChevronDown, ChevronUp, Target, AlertTriangle, Lightbulb } from "lucide-react";

interface CriterionScore {
  criterion_number: number;
  criterion_name: string;
  evidence_found: string[];
  strength: string;
  confidence: { data_confidence: number; criteria_match: number; overall: number; reasoning: string };
  gaps: string[];
  priority_actions: string[];
}

export function CriterionCard({ criterion }: { criterion: CriterionScore }) {
  const [expanded, setExpanded] = useState(false);

  const strengthColors = {
    strong: "bg-green-100 text-green-800 border-green-200",
    moderate: "bg-amber-100 text-amber-800 border-amber-200",
    weak: "bg-orange-100 text-orange-800 border-orange-200",
    none: "bg-red-100 text-red-800 border-red-200",
  };

  const strengthColor = strengthColors[criterion.strength as keyof typeof strengthColors] || strengthColors.none;

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div>
            <CardTitle className="text-base">
              {criterion.criterion_number}. {criterion.criterion_name}
            </CardTitle>
          </div>
          <div className="flex items-center gap-2">
            <Badge className={strengthColor} variant="outline">
              {criterion.strength.toUpperCase()}
            </Badge>
            <ConfidenceBadge confidence={criterion.confidence.overall} />
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        {/* Evidence found */}
        {criterion.evidence_found.length > 0 && (
          <div>
            <div className="flex items-center gap-1 text-sm font-medium text-green-700 mb-1">
              <Target className="h-3.5 w-3.5" /> Evidence Found
            </div>
            <ul className="text-sm text-muted-foreground space-y-0.5">
              {criterion.evidence_found.map((e, i) => (
                <li key={i}>• {e}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Gaps */}
        {criterion.gaps.length > 0 && (
          <div>
            <div className="flex items-center gap-1 text-sm font-medium text-amber-700 mb-1">
              <AlertTriangle className="h-3.5 w-3.5" /> Gaps
            </div>
            <ul className="text-sm text-muted-foreground space-y-0.5">
              {criterion.gaps.map((g, i) => (
                <li key={i}>• {g}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Priority Actions */}
        {criterion.priority_actions.length > 0 && (
          <div>
            <div className="flex items-center gap-1 text-sm font-medium text-primary mb-1">
              <Lightbulb className="h-3.5 w-3.5" /> Priority Actions
            </div>
            <ul className="text-sm text-muted-foreground space-y-0.5">
              {criterion.priority_actions.map((a, i) => (
                <li key={i}>• {a}</li>
              ))}
            </ul>
          </div>
        )}

        {/* AI Reasoning (expandable) */}
        <Button
          variant="ghost"
          size="sm"
          className="w-full text-xs"
          onClick={() => setExpanded(!expanded)}
        >
          {expanded ? <ChevronUp className="h-3 w-3 mr-1" /> : <ChevronDown className="h-3 w-3 mr-1" />}
          {expanded ? "Hide" : "Show"} AI Reasoning
        </Button>
        {expanded && (
          <div className="rounded-md bg-muted p-3 text-sm text-muted-foreground">
            <p>{criterion.confidence.reasoning}</p>
            <div className="mt-2 flex gap-4 text-xs">
              <span>Data Confidence: {criterion.confidence.data_confidence}%</span>
              <span>Criteria Match: {criterion.confidence.criteria_match}%</span>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
