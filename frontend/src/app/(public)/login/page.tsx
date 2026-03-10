"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Compass, Eye, EyeOff } from "lucide-react";
import { apiClient } from "@/lib/api";
import { useAuthStore } from "@/lib/store";

export default function LoginPage() {
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
    email: email.length === 0
      ? "Email is required"
      : !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
        ? "Please enter a valid email address"
        : null,
    password: password.length === 0 ? "Password is required" : null,
  };

  const hasValidationErrors = Object.values(validationErrors).some(Boolean);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setTouched({ email: true, password: true });
    if (hasValidationErrors) return;
    setError("");
    setLoading(true);
    try {
      const data = await apiClient.post<{
        access_token: string;
        user_id: string;
        name: string;
        onboarding_completed: boolean;
      }>("/api/auth/login", { email, password });
      setAuth(data.access_token, data.user_id, data.name, data.onboarding_completed);
      apiClient.setToken(data.access_token);
      router.push(data.onboarding_completed ? "/dashboard" : "/onboarding");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Login failed");
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
          <CardTitle className="text-2xl">Welcome back</CardTitle>
          <CardDescription>Log in to your immigration roadmap</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4" aria-label="Login form">
            {error && (
              <div role="alert" className="text-sm text-destructive bg-destructive/10 rounded-md p-3">
                {error}
              </div>
            )}
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
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  onBlur={() => markTouched("password")}
                  aria-invalid={touched.password && !!validationErrors.password}
                  aria-describedby={touched.password && validationErrors.password ? "password-error" : undefined}
                  required
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
              {loading ? "Logging in..." : "Log in"}
            </Button>
          </form>
          <p className="text-center text-sm text-muted-foreground mt-4">
            Don&apos;t have an account?{" "}
            <Link href="/register" className="text-primary hover:underline">
              Create one
            </Link>
          </p>
        </CardContent>
      </Card>
    </main>
  );
}
