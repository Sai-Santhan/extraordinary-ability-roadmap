"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Compass, Eye, EyeOff, Shield } from "lucide-react";
import { apiClient } from "@/lib/api";
import { useAuthStore } from "@/lib/store";

export default function RegisterPage() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [touched, setTouched] = useState<Record<string, boolean>>({});
  const router = useRouter();
  const setAuth = useAuthStore((s) => s.setAuth);

  const markTouched = (field: string) => setTouched((prev) => ({ ...prev, [field]: true }));

  const validationErrors = {
    name: name.trim().length === 0 ? "Full name is required" : null,
    email: email.length === 0
      ? "Email is required"
      : !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
        ? "Please enter a valid email address"
        : null,
    password: password.length === 0
      ? "Password is required"
      : password.length < 8
        ? "Password must be at least 8 characters"
        : !/[a-zA-Z]/.test(password)
          ? "Password must contain at least one letter"
          : !/[0-9]/.test(password)
            ? "Password must contain at least one number"
            : null,
  };

  const hasValidationErrors = Object.values(validationErrors).some(Boolean);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setTouched({ name: true, email: true, password: true });
    if (hasValidationErrors) return;
    setError("");
    setLoading(true);
    try {
      const data = await apiClient.post<{
        access_token: string;
        user_id: string;
        name: string;
        onboarding_completed: boolean;
      }>("/api/auth/register", { email, password, name });
      setAuth(data.access_token, data.user_id, data.name, data.onboarding_completed);
      apiClient.setToken(data.access_token);
      router.push(data.onboarding_completed ? "/dashboard" : "/onboarding");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Registration failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="flex items-center justify-center min-h-screen px-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <div className="flex justify-center mb-4" aria-hidden="true">
            <div className="h-12 w-12 rounded-xl bg-primary flex items-center justify-center">
              <Compass className="h-6 w-6 text-primary-foreground" />
            </div>
          </div>
          <CardTitle className="text-2xl">Create your account</CardTitle>
          <CardDescription>Start building your immigration roadmap</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4" aria-label="Registration form">
            {error && (
              <div role="alert" className="text-sm text-destructive bg-destructive/10 rounded-md p-3">
                {error}
              </div>
            )}
            <div className="space-y-2">
              <Label htmlFor="name">Full Name</Label>
              <Input
                id="name"
                placeholder="Dr. Jane Smith"
                value={name}
                onChange={(e) => setName(e.target.value)}
                onBlur={() => markTouched("name")}
                aria-invalid={touched.name && !!validationErrors.name}
                aria-describedby={touched.name && validationErrors.name ? "name-error" : undefined}
                required
              />
              {touched.name && validationErrors.name && (
                <p id="name-error" className="text-xs text-destructive">{validationErrors.name}</p>
              )}
            </div>
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                onBlur={() => markTouched("email")}
                aria-invalid={touched.email && !!validationErrors.email}
                aria-describedby={touched.email && validationErrors.email ? "email-error" : undefined}
                required
              />
              {touched.email && validationErrors.email && (
                <p id="email-error" className="text-xs text-destructive">{validationErrors.email}</p>
              )}
            </div>
            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <div className="relative">
                <Input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  placeholder="At least 8 characters"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  onBlur={() => markTouched("password")}
                  aria-invalid={touched.password && !!validationErrors.password}
                  aria-describedby={touched.password && validationErrors.password ? "password-error" : undefined}
                  required
                  minLength={8}
                />
                <button
                  type="button"
                  className="absolute right-2 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground p-1"
                  onClick={() => setShowPassword(!showPassword)}
                  aria-label={showPassword ? "Hide password" : "Show password"}
                >
                  {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
              {touched.password && validationErrors.password && (
                <p id="password-error" className="text-xs text-destructive">{validationErrors.password}</p>
              )}
            </div>
            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? "Creating account..." : "Create account"}
            </Button>
          </form>

          {/* Data handling notice */}
          <div className="mt-4 rounded-lg bg-muted p-3 text-xs text-muted-foreground">
            <div className="flex items-start gap-2">
              <Shield className="h-4 w-4 mt-0.5 text-primary shrink-0" />
              <div>
                <p className="font-medium text-foreground">How we handle your data</p>
                <ul className="mt-1 space-y-1">
                  <li>Your data is only processed when you explicitly upload it</li>
                  <li>We ask for your consent before sending anything to AI</li>
                  <li>You can export or delete all your data at any time</li>
                  <li>We never share your data with third parties</li>
                </ul>
              </div>
            </div>
          </div>

          <p className="text-center text-sm text-muted-foreground mt-4">
            Already have an account?{" "}
            <Link href="/login" className="text-primary hover:underline">
              Log in
            </Link>
          </p>
        </CardContent>
      </Card>
    </main>
  );
}
