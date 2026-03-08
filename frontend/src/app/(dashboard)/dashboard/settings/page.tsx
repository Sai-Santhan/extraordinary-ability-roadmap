"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
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
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Separator } from "@/components/ui/separator";
import { Shield, Trash2, X, User } from "lucide-react";
import { apiClient } from "@/lib/api";
import { useAuthStore } from "@/lib/store";

interface Consent {
  id: string;
  source_type: string;
  consent_given: boolean;
  consent_timestamp: string | null;
  processing_description: string;
}

export default function SettingsPage() {
  const [consents, setConsents] = useState<Consent[]>([]);
  const [deleteOpen, setDeleteOpen] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const router = useRouter();
  const { userName, clearAuth } = useAuthStore();

  useEffect(() => {
    apiClient
      .get<Consent[]>("/api/consent/")
      .then(setConsents)
      .catch(() => {});
  }, []);

  const handleRevoke = async (sourceType: string) => {
    try {
      await apiClient.delete(`/api/consent/${sourceType}`);
      setConsents((prev) => prev.filter((c) => c.source_type !== sourceType));
    } catch {
      // Handle error
    }
  };

  const handleDeleteAllData = async () => {
    setDeleting(true);
    try {
      await apiClient.delete("/api/data/me");
      clearAuth();
      apiClient.clearToken();
      router.push("/");
    } catch {
      // Handle error
    } finally {
      setDeleting(false);
    }
  };

  return (
    <div className="space-y-6 max-w-2xl">
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold">Settings</h1>
        <p className="text-muted-foreground mt-1">
          Manage your profile, consents, and data
        </p>
      </div>

      {/* Profile Info */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <User className="h-5 w-5" aria-hidden="true" />
            <CardTitle>Profile</CardTitle>
          </div>
        </CardHeader>
        <CardContent>
          <p className="text-sm">
            <span className="text-muted-foreground">Name:</span>{" "}
            <span className="font-medium">{userName || "Unknown"}</span>
          </p>
        </CardContent>
      </Card>

      {/* Active Consents */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Shield className="h-5 w-5 text-primary" aria-hidden="true" />
            <CardTitle>Active Consents</CardTitle>
          </div>
          <CardDescription>
            Data sources you&apos;ve given permission to process
          </CardDescription>
        </CardHeader>
        <CardContent>
          {consents.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              No active consents. Consent is requested when you upload data.
            </p>
          ) : (
            <div className="space-y-3">
              {consents.map((consent) => (
                <div
                  key={consent.id}
                  className="flex items-center justify-between rounded-lg border p-3"
                >
                  <div>
                    <p className="font-medium text-sm capitalize">
                      {consent.source_type.replace("_", " ")}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      Consented:{" "}
                      {consent.consent_timestamp
                        ? new Date(consent.consent_timestamp).toLocaleString()
                        : "Unknown"}
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant="outline" className="text-green-700 dark:text-green-400 bg-green-50 dark:bg-green-950/30">
                      Active
                    </Badge>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleRevoke(consent.source_type)}
                      aria-label={`Revoke consent for ${consent.source_type.replace("_", " ")}`}
                    >
                      <X className="h-4 w-4" aria-hidden="true" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      <Separator />

      {/* Danger Zone */}
      <Card className="border-red-200 dark:border-red-800">
        <CardHeader>
          <div className="flex items-center gap-2">
            <Trash2 className="h-5 w-5 text-red-600" aria-hidden="true" />
            <CardTitle className="text-red-600">Delete All Data</CardTitle>
          </div>
          <CardDescription>
            Permanently delete your account, all profiles, uploaded files,
            assessments, and roadmaps. This action cannot be undone.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Dialog open={deleteOpen} onOpenChange={setDeleteOpen}>
            <DialogTrigger render={<Button variant="destructive" />}>
              Delete All My Data
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Are you absolutely sure?</DialogTitle>
                <DialogDescription>
                  This will permanently delete your account and all associated
                  data including:
                  <ul className="mt-2 list-disc list-inside space-y-1">
                    <li>Your immigration profile</li>
                    <li>All uploaded evidence files</li>
                    <li>Criteria assessments and roadmaps</li>
                    <li>All consent records</li>
                  </ul>
                  <br />
                  This action cannot be undone.
                </DialogDescription>
              </DialogHeader>
              <DialogFooter>
                <Button
                  variant="outline"
                  onClick={() => setDeleteOpen(false)}
                >
                  Cancel
                </Button>
                <Button
                  variant="destructive"
                  onClick={handleDeleteAllData}
                  disabled={deleting}
                >
                  {deleting ? "Deleting..." : "Yes, delete everything"}
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </CardContent>
      </Card>
    </div>
  );
}
