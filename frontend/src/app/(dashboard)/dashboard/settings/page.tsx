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
import { Shield, Trash2, X, User, Compass, AlertCircle } from "lucide-react";
import { apiClient } from "@/lib/api";
import { useAuthStore } from "@/lib/store";

const PATHWAY_OPTIONS = [
  { value: "eb1a", label: "EB-1A: Extraordinary Ability" },
  { value: "eb1b", label: "EB-1B: Outstanding Researchers" },
  { value: "eb1c", label: "EB-1C: Multinational Managers" },
  { value: "niw", label: "NIW: National Interest Waiver" },
  { value: "o1", label: "O-1: Extraordinary Ability Visa" },
];

interface Consent {
  id: string;
  source_type: string;
  consent_given: boolean;
  consent_timestamp: string | null;
  processing_description: string;
}

interface Profile {
  id: string;
  target_pathway: string | null;
  last_pathway_switch: string | null;
}

export default function SettingsPage() {
  const [consents, setConsents] = useState<Consent[]>([]);
  const [deleteOpen, setDeleteOpen] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [profile, setProfile] = useState<Profile | null>(null);
  const [switchOpen, setSwitchOpen] = useState(false);
  const [selectedPathway, setSelectedPathway] = useState("");
  const [switching, setSwitching] = useState(false);
  const [switchError, setSwitchError] = useState("");
  const router = useRouter();
  const { userName, clearAuth } = useAuthStore();

  useEffect(() => {
    apiClient
      .get<Consent[]>("/api/consent/")
      .then(setConsents)
      .catch(() => {});
    apiClient
      .get<Profile[]>("/api/profiles/")
      .then((profiles) => {
        if (profiles.length > 0) setProfile(profiles[0]);
      })
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

  const canSwitchToday = () => {
    if (!profile?.last_pathway_switch) return true;
    const lastSwitch = new Date(profile.last_pathway_switch);
    const now = new Date();
    return now.getTime() - lastSwitch.getTime() > 24 * 60 * 60 * 1000;
  };

  const getNextSwitchTime = () => {
    if (!profile?.last_pathway_switch) return null;
    const next = new Date(new Date(profile.last_pathway_switch).getTime() + 24 * 60 * 60 * 1000);
    const now = new Date();
    const diff = next.getTime() - now.getTime();
    if (diff <= 0) return null;
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    return `${hours}h ${minutes}m`;
  };

  const handlePathwaySwitch = async () => {
    if (!profile || !selectedPathway) return;
    setSwitching(true);
    setSwitchError("");
    try {
      const result = await apiClient.patch<{
        target_pathway: string;
        last_pathway_switch: string;
      }>(`/api/profiles/${profile.id}/pathway`, { pathway: selectedPathway });
      setProfile((prev) => prev ? { ...prev, target_pathway: result.target_pathway, last_pathway_switch: result.last_pathway_switch } : prev);
      setSwitchOpen(false);
    } catch (err: unknown) {
      if (err instanceof Error && err.message.includes("429")) {
        setSwitchError("You can only switch pathways once per day.");
      } else {
        setSwitchError(err instanceof Error ? err.message : "Failed to switch pathway");
      }
    } finally {
      setSwitching(false);
    }
  };

  const currentPathway = PATHWAY_OPTIONS.find((p) => p.value === profile?.target_pathway);
  const switchAvailable = canSwitchToday();
  const nextSwitchIn = getNextSwitchTime();

  return (
    <div className="space-y-6 max-w-2xl">
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold">Settings</h1>
        <p className="text-muted-foreground mt-1">
          Manage your profile, pathway, consents, and data
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

      {/* Target Pathway */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Compass className="h-5 w-5 text-primary" aria-hidden="true" />
            <CardTitle>Target Pathway</CardTitle>
          </div>
          <CardDescription>
            Your current immigration pathway target. You can switch once per day.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">{currentPathway?.label || "Not set"}</p>
              {profile?.last_pathway_switch && (
                <p className="text-xs text-muted-foreground">
                  Last changed: {new Date(profile.last_pathway_switch).toLocaleDateString()}
                </p>
              )}
            </div>
            <Dialog open={switchOpen} onOpenChange={setSwitchOpen}>
              <DialogTrigger
                render={
                  <Button
                    variant="outline"
                    size="sm"
                    disabled={!switchAvailable}
                  />
                }
              >
                {switchAvailable ? "Change Pathway" : `Available in ${nextSwitchIn}`}
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Change Target Pathway</DialogTitle>
                  <DialogDescription>
                    You can only switch pathways once per day. This will require
                    re-running analysis to update your criteria assessment and roadmap.
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-2 py-4">
                  {PATHWAY_OPTIONS.map((option) => (
                    <button
                      key={option.value}
                      onClick={() => setSelectedPathway(option.value)}
                      disabled={option.value === profile?.target_pathway}
                      className={`w-full flex items-center gap-3 rounded-lg border-2 p-3 text-left transition-all ${
                        selectedPathway === option.value
                          ? "border-primary bg-primary/5"
                          : option.value === profile?.target_pathway
                            ? "border-muted opacity-50 cursor-not-allowed"
                            : "border-muted hover:border-primary/30"
                      }`}
                    >
                      <span className="font-medium text-sm">{option.label}</span>
                      {option.value === profile?.target_pathway && (
                        <Badge variant="secondary" className="ml-auto text-xs">Current</Badge>
                      )}
                    </button>
                  ))}
                </div>
                {switchError && (
                  <div className="flex items-center gap-2 text-sm text-destructive">
                    <AlertCircle className="h-4 w-4" />
                    {switchError}
                  </div>
                )}
                <DialogFooter>
                  <Button variant="outline" onClick={() => setSwitchOpen(false)}>Cancel</Button>
                  <Button
                    onClick={handlePathwaySwitch}
                    disabled={!selectedPathway || selectedPathway === profile?.target_pathway || switching}
                  >
                    {switching ? "Switching..." : "Confirm Switch"}
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </div>
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
