"use client";

import { useEffect, useState } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  FileJson,
  FileText,
  FileType,
  FileDown,
  Download,
  Loader2,
} from "lucide-react";
import { apiClient } from "@/lib/api";

const EXPORT_FORMATS = [
  {
    format: "json",
    name: "JSON",
    icon: FileJson,
    description: "Machine-readable structured data. Portable to other tools and attorney software.",
    mime: "application/json",
    ext: "json",
  },
  {
    format: "markdown",
    name: "Markdown",
    icon: FileText,
    description: "Human-readable summary. Great for personal records and version control.",
    mime: "text/markdown",
    ext: "md",
  },
  {
    format: "pdf",
    name: "PDF",
    icon: FileType,
    description: "Polished report with assessment summary. Ideal for attorney consultations.",
    mime: "application/pdf",
    ext: "pdf",
  },
  {
    format: "docx",
    name: "DOCX",
    icon: FileDown,
    description: "Editable Word document. Perfect for attorney markup and collaboration.",
    mime: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ext: "docx",
  },
];

interface Profile {
  id: string;
  status: string;
}

export default function ExportPage() {
  const [profileId, setProfileId] = useState<string | null>(null);
  const [profileStatus, setProfileStatus] = useState<string>("none");
  const [downloading, setDownloading] = useState<string | null>(null);

  useEffect(() => {
    apiClient
      .get<Profile[]>("/api/profiles/")
      .then((profiles) => {
        if (profiles.length > 0) {
          setProfileId(profiles[0].id);
          setProfileStatus(profiles[0].status);
        }
      })
      .catch(() => {});
  }, []);

  const handleExport = async (format: string, ext: string) => {
    if (!profileId) return;
    setDownloading(format);
    try {
      const blob = await apiClient.downloadFile(
        `/api/export/${profileId}?format=${format}`
      );
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `immigration-profile.${ext}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch {
      // Handle error
    } finally {
      setDownloading(null);
    }
  };

  const isComplete = profileStatus === "complete";

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold">Export Center</h1>
        <p className="text-muted-foreground mt-1">
          Download your immigration profile in portable, open formats. Your data is yours.
        </p>
      </div>

      {!isComplete && (
        <Card className="border-amber-200 dark:border-amber-800 bg-amber-50 dark:bg-amber-950/30">
          <CardContent className="pt-6">
            <p className="text-sm text-amber-800 dark:text-amber-200" role="status">
              Complete the AI analysis first to export your full profile. Current
              status: <Badge variant="secondary">{profileStatus}</Badge>
            </p>
          </CardContent>
        </Card>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {EXPORT_FORMATS.map((fmt) => (
          <Card key={fmt.format}>
            <CardHeader>
              <div className="flex items-center gap-3">
                <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center" aria-hidden="true">
                  <fmt.icon className="h-5 w-5 text-primary" />
                </div>
                <div>
                  <CardTitle className="text-base">{fmt.name}</CardTitle>
                  <CardDescription className="text-xs">
                    .{fmt.ext} format
                  </CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-3">
              <p className="text-sm text-muted-foreground">
                {fmt.description}
              </p>
              <Button
                className="w-full"
                variant={isComplete ? "default" : "secondary"}
                disabled={!isComplete || downloading === fmt.format}
                onClick={() => handleExport(fmt.format, fmt.ext)}
              >
                {downloading === fmt.format ? (
                  <Loader2 className="h-4 w-4 animate-spin mr-2" aria-hidden="true" />
                ) : (
                  <Download className="h-4 w-4 mr-2" aria-hidden="true" />
                )}
                Download {fmt.name}
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>

      <p className="text-xs text-muted-foreground text-center">
        All exports include the required disclaimer: &quot;This is not legal
        advice. Consult a qualified immigration attorney.&quot;
      </p>
    </div>
  );
}
