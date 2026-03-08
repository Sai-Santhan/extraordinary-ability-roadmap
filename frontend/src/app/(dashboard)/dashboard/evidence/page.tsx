"use client";

import { useCallback, useEffect, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Upload,
  FileText,
  Mail,
  Calendar,
  Github,
  Linkedin,
  MessageSquare,
  BookOpen,
  Play,
  CheckCircle2,
  Loader2,
  AlertCircle,
  Trash2,
  Eye,
  EyeOff,
  Plus,
  Image,
} from "lucide-react";
import { ConsentModal } from "@/components/consent-modal";
import { apiClient } from "@/lib/api";
import { useAuthStore, useAnalysisStore } from "@/lib/store";

const DATA_SOURCES = [
  { type: "cv", name: "CV / Resume", icon: FileText, accept: ".pdf,.txt,.docx", description: "Upload your CV or resume" },
  { type: "scholar", name: "Google Scholar", icon: BookOpen, accept: ".json", description: "Scholar publication data (JSON)" },
  { type: "github", name: "GitHub Profile", icon: Github, accept: ".json", description: "GitHub contributions data (JSON)" },
  { type: "gmail", name: "Gmail (MBOX)", icon: Mail, accept: ".mbox", description: "Google Takeout email archive" },
  { type: "calendar", name: "Calendar (ICS)", icon: Calendar, accept: ".ics", description: "Google Calendar events" },
  { type: "linkedin", name: "LinkedIn PDF", icon: Linkedin, accept: ".pdf,.txt", description: "LinkedIn profile export" },
  { type: "chatgpt_export", name: "ChatGPT Export", icon: MessageSquare, accept: ".json", description: "ChatGPT conversation history" },
  { type: "documents", name: "Other Documents", icon: Image, accept: ".pdf,.jpg,.jpeg,.png,.webp", description: "Certificates, awards, letters, articles (PDF or images)" },
];

interface UploadedFile {
  id: string;
  filename: string;
  source_type: string;
  extracted_preview: string;
  file_type?: string;
  uploaded_at?: string;
}

interface Consent {
  source_type: string;
  consent_given: boolean;
}

export default function EvidencePage() {
  const [profileId, setProfileId] = useState<string | null>(null);
  const [consents, setConsents] = useState<Consent[]>([]);
  const [consentModal, setConsentModal] = useState<{ open: boolean; type: string; name: string }>({ open: false, type: "", name: "" });
  const [uploads, setUploads] = useState<UploadedFile[]>([]);
  const [uploading, setUploading] = useState<string | null>(null);
  const [removing, setRemoving] = useState<string | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [previewId, setPreviewId] = useState<string | null>(null);
  const [pendingFile, setPendingFile] = useState<{ sourceType: string; file: File } | null>(null);
  const [eventSourceRef, setEventSourceRef] = useState<EventSource | null>(null);
  const [rateLimitMessage, setRateLimitMessage] = useState<string | null>(null);
  const token = useAuthStore((s) => s.token);
  const { stages, setStage, setProfileId: setAnalysisProfileId, reset: resetAnalysis } = useAnalysisStore();

  useEffect(() => {
    const init = async () => {
      try {
        const profiles = await apiClient.get<{ id: string }[]>("/api/profiles/");
        let pid: string;
        if (profiles.length > 0) {
          pid = profiles[0].id;
        } else {
          const newProfile = await apiClient.post<{ id: string }>("/api/profiles/");
          pid = newProfile.id;
        }
        setProfileId(pid);

        const existingEvidence = await apiClient.get<UploadedFile[]>(`/api/evidence/${pid}`);
        if (existingEvidence.length > 0) {
          setUploads(existingEvidence);
        }

        const c = await apiClient.get<Consent[]>("/api/consent/");
        setConsents(c);
      } catch {
        // Handle error
      }
    };
    init();
  }, []);

  const hasConsent = useCallback(
    (sourceType: string) => consents.some((c) => c.source_type === sourceType && c.consent_given),
    [consents]
  );

  const handleFileSelect = async (sourceType: string, sourceName: string, file: File) => {
    if (!hasConsent(sourceType)) {
      setPendingFile({ sourceType, file });
      setConsentModal({ open: true, type: sourceType, name: sourceName });
      return;
    }
    await uploadFile(sourceType, file);
  };

  const uploadFile = async (sourceType: string, file: File) => {
    if (!profileId) return;
    setUploading(sourceType);
    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("source_type", sourceType);
      formData.append("profile_id", profileId);
      const result = await apiClient.uploadFile<UploadedFile>("/api/evidence/upload", formData);
      setUploads((prev) => [...prev, result]);
    } catch {
      // Handle error
    } finally {
      setUploading(null);
    }
  };

  const removeEvidence = async (evidenceId: string) => {
    setRemoving(evidenceId);
    try {
      await apiClient.delete(`/api/evidence/${evidenceId}`);
      setUploads((prev) => prev.filter((u) => u.id !== evidenceId));
      if (previewId === evidenceId) setPreviewId(null);
    } catch {
      // Handle error
    } finally {
      setRemoving(null);
    }
  };

  const handleConsentGranted = async () => {
    setConsents((prev) => [...prev, { source_type: consentModal.type, consent_given: true }]);
    // Auto-upload the file that was pending consent
    if (pendingFile && pendingFile.sourceType === consentModal.type) {
      const { sourceType, file } = pendingFile;
      setPendingFile(null);
      await uploadFile(sourceType, file);
    }
  };

  const startAnalysis = async () => {
    if (!profileId || uploads.length === 0) return;
    setAnalyzing(true);
    setRateLimitMessage(null);
    resetAnalysis();
    setAnalysisProfileId(profileId);

    // Fetch a short-lived, scoped SSE token instead of exposing the main JWT in the URL
    let sseToken: string;
    try {
      const { sse_token } = await apiClient.post<{ sse_token: string }>(`/api/analyze/token/${profileId}`);
      sseToken = sse_token;
    } catch (err) {
      setAnalyzing(false);
      const message = err instanceof Error ? err.message : "Failed to start analysis";
      if (message.toLowerCase().includes("once per day") || message.toLowerCase().includes("rate limit") || message.includes("24 hours")) {
        setRateLimitMessage(message);
      }
      return;
    }

    const API_BASE = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";
    const eventSource = new EventSource(`${API_BASE}/api/analyze/stream/${profileId}?token=${sseToken}`);
    setEventSourceRef(eventSource);

    eventSource.addEventListener("stage", (e) => {
      const data = JSON.parse(e.data);
      setStage(data.stage, data.status);
    });

    const cleanup = () => {
      setAnalyzing(false);
      setEventSourceRef(null);
      eventSource.close();
    };

    eventSource.addEventListener("complete", cleanup);
    eventSource.addEventListener("error", cleanup);
    eventSource.onerror = cleanup;
  };

  const stopAnalysis = () => {
    if (eventSourceRef) {
      eventSourceRef.close();
      setEventSourceRef(null);
    }
    setAnalyzing(false);
  };

  const stageIcons: Record<string, React.ReactNode> = {
    pending: <div className="h-5 w-5 rounded-full border-2 border-muted" aria-hidden="true" />,
    started: <Loader2 className="h-5 w-5 animate-spin text-primary" aria-hidden="true" />,
    completed: <CheckCircle2 className="h-5 w-5 text-green-600" aria-hidden="true" />,
    error: <AlertCircle className="h-5 w-5 text-red-600" aria-hidden="true" />,
  };

  const stageLabels: Record<string, string> = {
    pending: "Pending",
    started: "In progress",
    completed: "Completed",
    error: "Error",
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold">Evidence Upload</h1>
        <p className="text-muted-foreground mt-1">
          Upload your career data. You can add multiple files per source.
        </p>
      </div>

      {/* Upload Sources */}
      <section aria-label="Data sources">
        <h2 className="sr-only">Upload data sources</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {DATA_SOURCES.map((source) => {
            const sourceFiles = uploads.filter((u) => u.source_type === source.type);
            const isUploading = uploading === source.type;
            const consented = hasConsent(source.type);
            const hasFiles = sourceFiles.length > 0;

            return (
              <Card key={source.type} className={hasFiles ? "border-green-200 dark:border-green-800 bg-green-50/50 dark:bg-green-950/20" : ""}>
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <source.icon className="h-5 w-5 text-muted-foreground" aria-hidden="true" />
                      <CardTitle className="text-base">{source.name}</CardTitle>
                    </div>
                    <div className="flex items-center gap-1.5">
                      {hasFiles && (
                        <Badge variant="secondary" className="text-xs">
                          {sourceFiles.length} file{sourceFiles.length > 1 ? "s" : ""}
                        </Badge>
                      )}
                      {consented && (
                        <Badge variant="outline" className="text-xs">
                          <span className="sr-only">Consent status:</span>
                          Consented
                        </Badge>
                      )}
                    </div>
                  </div>
                  <CardDescription className="text-xs">{source.description}</CardDescription>
                </CardHeader>
                <CardContent className="space-y-3">
                  {/* List of uploaded files */}
                  {sourceFiles.length > 0 && (
                    <div className="space-y-2" role="list" aria-label={`${source.name} files`}>
                      {sourceFiles.map((file) => {
                        const isPreviewing = previewId === file.id;
                        const isDeleting = removing === file.id;

                        return (
                          <div key={file.id} role="listitem" className="rounded-md border bg-background p-2.5">
                            <div className="flex items-center gap-2">
                              <FileText className="h-3.5 w-3.5 text-muted-foreground shrink-0" aria-hidden="true" />
                              <div className="min-w-0 flex-1">
                                <p className="text-sm font-medium truncate">{file.filename}</p>
                                <p className="text-xs text-muted-foreground">
                                  {file.file_type && <span className="uppercase">.{file.file_type}</span>}
                                  {file.uploaded_at && (
                                    <span>
                                      {file.file_type && " \u00b7 "}
                                      {new Date(file.uploaded_at).toLocaleDateString()}
                                    </span>
                                  )}
                                </p>
                              </div>
                              <div className="flex items-center gap-1 shrink-0">
                                <Button
                                  variant="ghost"
                                  size="icon"
                                  className="h-7 w-7"
                                  onClick={() => setPreviewId(isPreviewing ? null : file.id)}
                                  aria-expanded={isPreviewing}
                                  aria-controls={`preview-${file.id}`}
                                  aria-label={isPreviewing ? `Hide preview of ${file.filename}` : `Preview ${file.filename}`}
                                >
                                  {isPreviewing ? (
                                    <EyeOff className="h-3.5 w-3.5" aria-hidden="true" />
                                  ) : (
                                    <Eye className="h-3.5 w-3.5" aria-hidden="true" />
                                  )}
                                </Button>
                                <Button
                                  variant="ghost"
                                  size="icon"
                                  className="h-7 w-7 text-destructive hover:text-destructive"
                                  onClick={() => removeEvidence(file.id)}
                                  disabled={isDeleting}
                                  aria-label={`Delete ${file.filename}`}
                                >
                                  {isDeleting ? (
                                    <Loader2 className="h-3.5 w-3.5 animate-spin" aria-hidden="true" />
                                  ) : (
                                    <Trash2 className="h-3.5 w-3.5" aria-hidden="true" />
                                  )}
                                </Button>
                              </div>
                            </div>
                            {isPreviewing && (
                              <div
                                id={`preview-${file.id}`}
                                className="mt-2 rounded bg-muted p-2.5 text-xs text-muted-foreground whitespace-pre-wrap max-h-40 overflow-y-auto"
                                role="region"
                                aria-label={`Preview of ${file.filename}`}
                              >
                                {file.extracted_preview || "No preview available."}
                              </div>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  )}

                  {/* Upload area — always shown */}
                  <label
                    className={`flex items-center gap-2 rounded-lg cursor-pointer transition-colors ${
                      hasFiles
                        ? "p-2.5 border border-dashed hover:border-primary/30 hover:bg-primary/5 focus-within:ring-2 focus-within:ring-primary focus-within:ring-offset-2 justify-center"
                        : "flex-col p-4 border-2 border-dashed hover:border-primary/30 hover:bg-primary/5 focus-within:ring-2 focus-within:ring-primary focus-within:ring-offset-2"
                    }`}
                  >
                    {isUploading ? (
                      <Loader2 className={`animate-spin text-primary ${hasFiles ? "h-4 w-4" : "h-8 w-8"}`} aria-hidden="true" />
                    ) : hasFiles ? (
                      <Plus className="h-4 w-4 text-muted-foreground" aria-hidden="true" />
                    ) : (
                      <Upload className="h-8 w-8 text-muted-foreground" aria-hidden="true" />
                    )}
                    <span className={`text-muted-foreground text-center ${hasFiles ? "text-xs" : "text-xs"}`}>
                      {isUploading ? "Uploading..." : hasFiles ? "Add another file" : `Drop or click (${source.accept})`}
                    </span>
                    <input
                      type="file"
                      className="sr-only"
                      accept={source.accept}
                      aria-label={`Upload ${source.name} file`}
                      onChange={(e) => {
                        const file = e.target.files?.[0];
                        if (file) handleFileSelect(source.type, source.name, file);
                        e.target.value = "";
                      }}
                      disabled={isUploading}
                    />
                  </label>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </section>

      {/* Analysis Section */}
      {uploads.length > 0 && (
        <section aria-label="AI Analysis">
          <Card>
            <CardHeader>
              <CardTitle>Run AI Analysis</CardTitle>
              <CardDescription>
                Process your {uploads.length} uploaded file(s) through our 4-stage AI pipeline
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div
                className="grid grid-cols-2 sm:grid-cols-4 gap-3 sm:gap-4"
                role="list"
                aria-label="Analysis pipeline stages"
              >
                {(["ingestion", "extraction", "assessment", "roadmap"] as const).map((stage) => (
                  <div
                    key={stage}
                    className="flex items-center gap-2"
                    role="listitem"
                    aria-label={`${stage}: ${stageLabels[stages[stage]]}`}
                  >
                    {stageIcons[stages[stage]]}
                    <span className="text-sm capitalize">{stage}</span>
                  </div>
                ))}
              </div>

              {rateLimitMessage && (
                <div className="rounded-md bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-800 p-3 text-sm text-amber-800 dark:text-amber-200">
                  <AlertCircle className="h-4 w-4 inline mr-1.5" aria-hidden="true" />
                  {rateLimitMessage}
                </div>
              )}

              {analyzing ? (
                <Button
                  onClick={stopAnalysis}
                  variant="destructive"
                  className="w-full"
                >
                  <AlertCircle className="h-4 w-4 mr-2" aria-hidden="true" />
                  Stop Analysis
                </Button>
              ) : (
                <Button
                  onClick={startAnalysis}
                  className="w-full"
                  disabled={!!rateLimitMessage}
                >
                  <Play className="h-4 w-4 mr-2" aria-hidden="true" />
                  Start Analysis
                </Button>
              )}
            </CardContent>
          </Card>
        </section>
      )}

      <ConsentModal
        open={consentModal.open}
        onOpenChange={(open) => {
          setConsentModal((prev) => ({ ...prev, open }));
          if (!open) setPendingFile(null);
        }}
        sourceType={consentModal.type}
        sourceName={consentModal.name}
        onConsent={handleConsentGranted}
      />
    </div>
  );
}
