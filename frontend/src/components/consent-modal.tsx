"use client";

import { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Shield, AlertTriangle } from "lucide-react";
import { apiClient } from "@/lib/api";

interface ConsentModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  sourceType: string;
  sourceName: string;
  onConsent: () => void;
}

const SOURCE_DESCRIPTIONS: Record<string, { dataTypes: string[]; processing: string[] }> = {
  cv: {
    dataTypes: ["Name, contact info", "Work history, education", "Publications, awards", "Skills and certifications"],
    processing: ["Text extracted locally from your PDF/DOCX", "Extracted text sent to Anthropic's Claude AI for structured parsing", "Structured data stored in your private profile"],
  },
  scholar: {
    dataTypes: ["Publication titles and venues", "Citation counts, h-index", "Co-author names"],
    processing: ["Data fetched from Semantic Scholar API", "Publication metadata sent to Claude AI for criteria matching", "Results stored in your private profile"],
  },
  github: {
    dataTypes: ["Repository names and descriptions", "Star counts, contribution history", "Pull request and review activity"],
    processing: ["Data fetched from GitHub API", "Contribution data sent to Claude AI for criteria matching", "Results stored in your private profile"],
  },
  gmail: {
    dataTypes: ["Email subjects and senders", "Email body text", "Date and metadata"],
    processing: ["MBOX file parsed locally on our server", "Email content sent to Claude AI to classify immigration-relevant items", "Only classified results stored (not raw emails)"],
  },
  linkedin: {
    dataTypes: ["Work experience, education", "Skills and endorsements", "Recommendations text"],
    processing: ["PDF text extracted locally", "Extracted text sent to Claude AI for structured parsing", "Structured data stored in your private profile"],
  },
  chatgpt_export: {
    dataTypes: ["Conversation titles", "Message content (user and assistant)", "Timestamps"],
    processing: ["JSON file parsed locally", "Conversation content sent to Claude AI to identify career-relevant discussions", "Only relevant extracts stored"],
  },
  calendar: {
    dataTypes: ["Event titles and descriptions", "Dates and locations", "Attendee information"],
    processing: ["ICS file parsed locally", "Event data sent to Claude AI to identify speaking engagements and professional activities", "Classified events stored in your profile"],
  },
};

export function ConsentModal({
  open,
  onOpenChange,
  sourceType,
  sourceName,
  onConsent,
}: ConsentModalProps) {
  const [loading, setLoading] = useState(false);
  const info = SOURCE_DESCRIPTIONS[sourceType] || {
    dataTypes: ["File content"],
    processing: ["File processed locally", "Content sent to Claude AI for analysis"],
  };

  const handleConsent = async () => {
    setLoading(true);
    try {
      await apiClient.post("/api/consent/", {
        source_type: sourceType,
        consent_given: true,
        processing_description: `User consented to process ${sourceName} data. Data types: ${info.dataTypes.join(", ")}. Processing: ${info.processing.join("; ")}`,
      });
      onConsent();
      onOpenChange(false);
    } catch {
      // Handle error
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5 text-primary" aria-hidden="true" />
            Permission to Process {sourceName}
          </DialogTitle>
          <DialogDescription>
            Before we process your data, please review what will be accessed and how.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          <div>
            <h4 className="text-sm font-medium mb-2">Data that will be accessed:</h4>
            <ul className="text-sm text-muted-foreground space-y-1">
              {info.dataTypes.map((d, i) => (
                <li key={i} className="flex items-start gap-2">
                  <span className="text-primary mt-1">•</span> {d}
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h4 className="text-sm font-medium mb-2">How it will be processed:</h4>
            <ul className="text-sm text-muted-foreground space-y-1">
              {info.processing.map((p, i) => (
                <li key={i} className="flex items-start gap-2">
                  <span className="text-amber-500 mt-1">•</span> {p}
                </li>
              ))}
            </ul>
          </div>

          <div className="rounded-md bg-amber-50 dark:bg-amber-950/30 p-3 flex gap-2" role="alert">
            <AlertTriangle className="h-4 w-4 text-amber-600 mt-0.5 shrink-0" aria-hidden="true" />
            <p className="text-xs text-amber-800 dark:text-amber-200">
              Your data will be sent to Anthropic&apos;s Claude API for AI analysis.
              You can revoke consent and delete all data at any time from Settings.
            </p>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button onClick={handleConsent} disabled={loading}>
            {loading ? "Processing..." : "I Consent — Process My Data"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
