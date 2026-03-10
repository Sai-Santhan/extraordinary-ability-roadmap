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
import { Shield, Trash2, X, User, Compass, AlertCircle, Database } from "lucide-react";
import { apiClient } from "@/lib/api";
import { useAuthStore } from "@/lib/store";
import { toast } from "sonner";

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
  const [deleteDataOpen, setDeleteDataOpen] = useState(false);
  const [deletingData, setDeletingData] = useState(false);
  const [deleteAccountOpen, setDeleteAccountOpen] = useState(false);
  const [deletingAccount, setDeletingAccount] = useState(false);
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
      .catch(() => toast.error("Failed to load consents"));
    apiClient
      .get<Profile[]>("/api/profiles/")
      .then((profiles) => {
        if (profiles.length > 0) setProfile(profiles[0]);
      })
      .catch(() => toast.error("Failed to load profile"));
  }, []);

  const handleRevoke = async (sourceType: string) => {
    try {
      await apiClient.delete(`/api/consent/${sourceType}`);
      setConsents((prev) => prev.filter((c) => c.source_type !== sourceType));
      toast.success("Consent revoked");
    } catch {
      toast.error("Failed to revoke consent");
    }
  };

  const handleDeleteDataOnly = async () => {
    setDeletingData(true);
    try {
      await apiClient.delete("/api/data/me/data-only");
      toast.success("All data deleted. Your account is still active.");
      setDeleteDataOpen(false);
      setConsents([]);
      setProfile(null);
      router.push("/dashboard");
    } catch {
      toast.error("Failed to delete data. Please try again.");
    } finally {
      setDeletingData(false);
    }
  };

  const handleDeleteAccount = async () => {
    setDeletingAccount(true);
    try {
      await apiClient.delete("/api/data/me");
      toast.success("Account deleted");
      clearAuth();
      apiClient.clearToken();
      router.push("/");
    } catch {
      toast.error("Failed to delete account. Please try again.");
    } finally {
      setDeletingAccount(false);
    }
  };

  const canSwitchPathway = () => {
    if (!profile?.last_pathway_switch) return true;
    const lastSwitch = new Date(profile.last_pathway_switch);
    const now = new Date();
    return now.getTime() - lastSwitch.getTime() > 30 * 24 * 60 * 60 * 1000;
  };

  const getNextSwitchTime = () => {
    if (!profile?.last_pathway_switch) return null;
    const next = new Date(new Date(profile.last_pathway_switch).getTime() + 30 * 24 * 60 * 60 * 1000);
    const now = new Date();
    const diff = next.getTime() - now.getTime();
    if (diff <= 0) return null;
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    if (days > 0) return `${days}d`;
    const hours = Math.floor(diff / (1000 * 60 * 60));
    return `${hours}h`;
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
      toast.success("Pathway updated");
    } catch (err: unknown) {
      if (err instanceof Error && err.message.includes("429")) {
        setSwitchError("You can only switch pathways once per month.");
      } else {
        setSwitchError(err instanceof Error ? err.message : "Failed to switch pathway");
      }
    } finally {
      setSwitching(false);
    }
  };

  const currentPathway = PATHWAY_OPTIONS.find((p) => p.value === profile?.target_pathway);
  const switchAvailable = canSwitchPathway();
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
            Your current immigration pathway target. You can switch once per month.
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
                    You can only switch pathways once per month. This will require
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

      {/* Danger Zone — Delete Data */}
      <Card className="border-amber-200 dark:border-amber-800">
        <CardHeader>
          <div className="flex items-center gap-2">
            <Database className="h-5 w-5 text-amber-600" aria-hidden="true" />
            <CardTitle className="text-amber-600">Delete My Data</CardTitle>
          </div>
          <CardDescription>
            Delete all profiles, uploaded files, assessments, roadmaps, and consent records.
            Your account will remain active so you can start fresh.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Dialog open={deleteDataOpen} onOpenChange={setDeleteDataOpen}>
            <DialogTrigger render={<Button variant="outline" className="border-amber-300 text-amber-700 hover:bg-amber-50 dark:border-amber-700 dark:text-amber-400 dark:hover:bg-amber-950/30" />}>
              Delete My Data
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Delete all your data?</DialogTitle>
                <DialogDescription>
                  This will permanently delete:
                  <ul className="mt-2 list-disc list-inside space-y-1">
                    <li>Your immigration profile</li>
                    <li>All uploaded evidence files</li>
                    <li>Criteria assessments and roadmaps</li>
                    <li>All consent records</li>
                  </ul>
                  <br />
                  Your account will remain active. You can re-upload data and start fresh.
                </DialogDescription>
              </DialogHeader>
              <DialogFooter>
                <Button variant="outline" onClick={() => setDeleteDataOpen(false)}>
                  Cancel
                </Button>
                <Button
                  variant="destructive"
                  onClick={handleDeleteDataOnly}
                  disabled={deletingData}
                >
                  {deletingData ? "Deleting..." : "Yes, delete my data"}
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </CardContent>
      </Card>

      {/* Danger Zone — Delete Account */}
      <Card className="border-red-200 dark:border-red-800">
        <CardHeader>
          <div className="flex items-center gap-2">
            <Trash2 className="h-5 w-5 text-red-600" aria-hidden="true" />
            <CardTitle className="text-red-600">Delete Account</CardTitle>
          </div>
          <CardDescription>
            Permanently delete your account and all associated data.
            This action cannot be undone.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Dialog open={deleteAccountOpen} onOpenChange={setDeleteAccountOpen}>
            <DialogTrigger render={<Button variant="destructive" />}>
              Delete My Account
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Are you absolutely sure?</DialogTitle>
                <DialogDescription>
                  This will permanently delete your account and all associated
                  data including:
                  <ul className="mt-2 list-disc list-inside space-y-1">
                    <li>Your user account</li>
                    <li>Your immigration profile</li>
                    <li>All uploaded evidence files</li>
                    <li>Criteria assessments and roadmaps</li>
                    <li>All consent records</li>
                  </ul>
                  <br />
                  This action cannot be undone. You will need to create a new account.
                </DialogDescription>
              </DialogHeader>
              <DialogFooter>
                <Button variant="outline" onClick={() => setDeleteAccountOpen(false)}>
                  Cancel
                </Button>
                <Button
                  variant="destructive"
                  onClick={handleDeleteAccount}
                  disabled={deletingAccount}
                >
                  {deletingAccount ? "Deleting..." : "Yes, delete my account"}
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </CardContent>
      </Card>
    </div>
  );
}
