"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import {
  GraduationCap,
  Code,
  Briefcase,
  Rocket,
  HelpCircle,
  ArrowRight,
  ArrowLeft,
  CheckCircle2,
  Compass,
  Loader2,
} from "lucide-react";
import { apiClient } from "@/lib/api";
import { useAuthStore } from "@/lib/store";

const ROLE_OPTIONS = [
  { value: "researcher", label: "Researcher / Professor", icon: GraduationCap, description: "Academic or research-focused career" },
  { value: "engineer", label: "Software Engineer", icon: Code, description: "Technology and software development" },
  { value: "executive", label: "Executive / Manager", icon: Briefcase, description: "Leadership and management roles" },
  { value: "entrepreneur", label: "Entrepreneur", icon: Rocket, description: "Founded or co-founded a company" },
  { value: "other", label: "Other", icon: HelpCircle, description: "Another professional field" },
];

const QUALIFICATION_OPTIONS = [
  { value: "publications", label: "I have publications or citations in my field" },
  { value: "managerial", label: "I hold a managerial or executive position" },
  { value: "multinational", label: "I work for a multinational company" },
  { value: "job_offer", label: "I have a permanent US job offer" },
  { value: "awards", label: "I have received awards or recognition" },
];

const VISA_OPTIONS = [
  { value: "", label: "Skip this question" },
  { value: "h1b", label: "H-1B" },
  { value: "f1_opt", label: "F-1 / OPT" },
  { value: "l1", label: "L-1" },
  { value: "b1_b2", label: "B-1 / B-2" },
  { value: "j1", label: "J-1" },
  { value: "tn", label: "TN" },
  { value: "none", label: "None / Not in US" },
  { value: "other", label: "Other" },
];

const PATHWAY_LABELS: Record<string, { name: string; tagline: string }> = {
  eb1a: { name: "EB-1A", tagline: "Extraordinary Ability" },
  eb1b: { name: "EB-1B", tagline: "Outstanding Researchers" },
  eb1c: { name: "EB-1C", tagline: "Multinational Managers" },
  niw: { name: "NIW", tagline: "National Interest Waiver" },
  o1: { name: "O-1", tagline: "Extraordinary Ability Visa" },
};

interface Recommendation {
  recommended: string;
  match_score: number;
  explanation: string;
}

const TOTAL_STEPS = 6;

export default function OnboardingPage() {
  const [step, setStep] = useState(1);
  const [roleType, setRoleType] = useState("");
  const [primaryField, setPrimaryField] = useState("");
  const [yearsExperience, setYearsExperience] = useState<string>("");
  const [qualifications, setQualifications] = useState<string[]>([]);
  const [currentVisa, setCurrentVisa] = useState("");
  const [loading, setLoading] = useState(false);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [recommendedPathway, setRecommendedPathway] = useState("");
  const router = useRouter();
  const setOnboardingCompleted = useAuthStore((s) => s.setOnboardingCompleted);

  const toggleQualification = (value: string) => {
    setQualifications((prev) =>
      prev.includes(value) ? prev.filter((q) => q !== value) : [...prev, value]
    );
  };

  const canAdvance = () => {
    switch (step) {
      case 1: return !!roleType;
      case 2: return primaryField.trim().length > 0;
      case 3: return yearsExperience !== "" && Number(yearsExperience) >= 0;
      case 4: return true; // qualifications are optional
      case 5: return true; // visa is optional
      default: return false;
    }
  };

  const handleSubmit = async () => {
    setLoading(true);
    try {
      const data = await apiClient.post<{
        recommended_pathway: string;
        recommendations: Recommendation[];
        profile_id: string;
      }>("/api/onboarding/", {
        role_type: roleType,
        primary_field: primaryField,
        years_experience: Number(yearsExperience),
        qualifications,
        current_visa: currentVisa || null,
      });
      setRecommendedPathway(data.recommended_pathway);
      setRecommendations(data.recommendations);
      setOnboardingCompleted(true);
      setStep(6);
    } catch {
      // Handle error
    } finally {
      setLoading(false);
    }
  };

  const handleNext = () => {
    if (step === 5) {
      handleSubmit();
    } else {
      setStep((s) => s + 1);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-[calc(100vh-4rem)] px-4 py-8">
      <div className="w-full max-w-2xl space-y-6">
        {/* Progress */}
        {step < 6 && (
          <div className="space-y-2">
            <div className="flex justify-between text-sm text-muted-foreground">
              <span>Step {step} of {TOTAL_STEPS - 1}</span>
              <span>{Math.round((step / (TOTAL_STEPS - 1)) * 100)}%</span>
            </div>
            <div className="h-2 rounded-full bg-muted overflow-hidden">
              <div
                className="h-full bg-primary rounded-full transition-all duration-500 ease-out"
                style={{ width: `${(step / (TOTAL_STEPS - 1)) * 100}%` }}
              />
            </div>
          </div>
        )}

        {/* Step 1: Role */}
        {step === 1 && (
          <Card>
            <CardHeader>
              <CardTitle className="text-2xl">What best describes your role?</CardTitle>
              <CardDescription>This helps us recommend the right immigration pathway for you.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {ROLE_OPTIONS.map((option) => (
                <button
                  key={option.value}
                  onClick={() => setRoleType(option.value)}
                  className={`w-full flex items-center gap-4 rounded-xl border-2 p-4 text-left transition-all ${
                    roleType === option.value
                      ? "border-primary bg-primary/5 shadow-sm"
                      : "border-muted hover:border-primary/30 hover:bg-accent/50"
                  }`}
                >
                  <div className={`h-10 w-10 rounded-lg flex items-center justify-center shrink-0 ${
                    roleType === option.value ? "bg-primary text-primary-foreground" : "bg-muted"
                  }`}>
                    <option.icon className="h-5 w-5" />
                  </div>
                  <div>
                    <p className="font-medium">{option.label}</p>
                    <p className="text-sm text-muted-foreground">{option.description}</p>
                  </div>
                  {roleType === option.value && (
                    <CheckCircle2 className="h-5 w-5 text-primary ml-auto shrink-0" />
                  )}
                </button>
              ))}
            </CardContent>
          </Card>
        )}

        {/* Step 2: Field */}
        {step === 2 && (
          <Card>
            <CardHeader>
              <CardTitle className="text-2xl">What is your primary field of expertise?</CardTitle>
              <CardDescription>Be specific — this helps match you to the right USCIS criteria.</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <Label htmlFor="field">Field of expertise</Label>
                <Input
                  id="field"
                  placeholder="e.g., Machine Learning, Biotechnology, Finance"
                  value={primaryField}
                  onChange={(e) => setPrimaryField(e.target.value)}
                  className="text-lg py-6"
                  autoFocus
                />
              </div>
            </CardContent>
          </Card>
        )}

        {/* Step 3: Experience */}
        {step === 3 && (
          <Card>
            <CardHeader>
              <CardTitle className="text-2xl">How many years of professional experience?</CardTitle>
              <CardDescription>Count from the start of your career (including grad school research if applicable).</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <Label htmlFor="experience">Years of experience</Label>
                <Input
                  id="experience"
                  type="number"
                  min={0}
                  max={50}
                  value={yearsExperience}
                  onChange={(e) => {
                    const value = e.target.value;
                    if (value === '') {
                      setYearsExperience("");
                    } else {
                      const num = parseInt(value, 10);
                      if (!isNaN(num) && num >= 0 && num <= 50) {
                        setYearsExperience(String(num));
                      }
                    }
                  }}
                  className="text-lg py-6"
                  autoFocus
                />
              </div>
            </CardContent>
          </Card>
        )}

        {/* Step 4: Qualifications */}
        {step === 4 && (
          <Card>
            <CardHeader>
              <CardTitle className="text-2xl">Which of the following apply to you?</CardTitle>
              <CardDescription>Select all that apply. These help us assess pathway eligibility.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {QUALIFICATION_OPTIONS.map((option) => {
                const selected = qualifications.includes(option.value);
                return (
                  <button
                    key={option.value}
                    onClick={() => toggleQualification(option.value)}
                    className={`w-full flex items-center gap-3 rounded-xl border-2 p-4 text-left transition-all ${
                      selected
                        ? "border-primary bg-primary/5 shadow-sm"
                        : "border-muted hover:border-primary/30 hover:bg-accent/50"
                    }`}
                  >
                    <div className={`h-6 w-6 rounded-md border-2 flex items-center justify-center shrink-0 transition-colors ${
                      selected ? "border-primary bg-primary" : "border-muted-foreground/30"
                    }`}>
                      {selected && <CheckCircle2 className="h-4 w-4 text-primary-foreground" />}
                    </div>
                    <span className="font-medium">{option.label}</span>
                  </button>
                );
              })}
            </CardContent>
          </Card>
        )}

        {/* Step 5: Visa Status */}
        {step === 5 && (
          <Card>
            <CardHeader>
              <CardTitle className="text-2xl">What is your current visa status?</CardTitle>
              <CardDescription>Optional — helps us provide more relevant advice.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {VISA_OPTIONS.map((option) => (
                <button
                  key={option.value}
                  onClick={() => setCurrentVisa(option.value)}
                  className={`w-full flex items-center gap-3 rounded-xl border-2 p-3 text-left transition-all ${
                    currentVisa === option.value
                      ? "border-primary bg-primary/5 shadow-sm"
                      : "border-muted hover:border-primary/30 hover:bg-accent/50"
                  }`}
                >
                  <span className="font-medium">{option.label}</span>
                  {currentVisa === option.value && (
                    <CheckCircle2 className="h-5 w-5 text-primary ml-auto shrink-0" />
                  )}
                </button>
              ))}
            </CardContent>
          </Card>
        )}

        {/* Step 6: Results */}
        {step === 6 && (
          <div className="space-y-6">
            <div className="text-center space-y-2">
              <div className="flex justify-center">
                <div className="h-16 w-16 rounded-2xl bg-primary/10 flex items-center justify-center">
                  <Compass className="h-8 w-8 text-primary" />
                </div>
              </div>
              <h1 className="text-3xl font-bold">Your Recommended Pathway</h1>
              <p className="text-muted-foreground">Based on your profile, here&apos;s what we recommend.</p>
            </div>

            {recommendations.map((rec, i) => {
              const info = PATHWAY_LABELS[rec.recommended] || { name: rec.recommended.toUpperCase(), tagline: "" };
              const isTop = i === 0;
              return (
                <Card
                  key={rec.recommended}
                  className={isTop
                    ? "border-primary/50 bg-primary/5 shadow-md"
                    : "opacity-80"
                  }
                >
                  <CardContent className="pt-6">
                    <div className="flex items-start justify-between gap-4">
                      <div className="space-y-1 flex-1">
                        <div className="flex items-center gap-2">
                          <h3 className="text-lg font-bold">{info.name}: {info.tagline}</h3>
                          {isTop && <Badge>Recommended</Badge>}
                        </div>
                        <p className="text-sm text-muted-foreground">{rec.explanation}</p>
                      </div>
                      <div className="text-right shrink-0">
                        <p className="text-2xl font-bold text-primary">{rec.match_score}%</p>
                        <p className="text-xs text-muted-foreground">match</p>
                      </div>
                    </div>
                    <div className="mt-3 h-2 rounded-full bg-muted overflow-hidden">
                      <div
                        className={`h-full rounded-full transition-all duration-700 ${
                          isTop ? "bg-primary" : "bg-muted-foreground/30"
                        }`}
                        style={{ width: `${rec.match_score}%` }}
                      />
                    </div>
                  </CardContent>
                </Card>
              );
            })}

            <div className="space-y-3">
              <Button onClick={() => router.push("/dashboard")} className="w-full" size="lg">
                Continue to Dashboard
                <ArrowRight className="h-4 w-4 ml-2" />
              </Button>
              <p className="text-xs text-center text-muted-foreground">
                You can change your target pathway anytime from Settings.
              </p>
            </div>
          </div>
        )}

        {/* Navigation */}
        {step < 6 && (
          <div className="flex justify-between">
            <Button
              variant="outline"
              onClick={() => setStep((s) => s - 1)}
              disabled={step === 1}
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back
            </Button>
            <Button
              onClick={handleNext}
              disabled={!canAdvance() || loading}
            >
              {loading ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Analyzing...
                </>
              ) : step === 5 ? (
                <>
                  Get Recommendation
                  <ArrowRight className="h-4 w-4 ml-2" />
                </>
              ) : (
                <>
                  Next
                  <ArrowRight className="h-4 w-4 ml-2" />
                </>
              )}
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}
