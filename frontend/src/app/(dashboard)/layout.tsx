"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/lib/store";
import { DashboardSidebar } from "@/components/dashboard-sidebar";
import { SidebarProvider, SidebarInset, SidebarTrigger } from "@/components/ui/sidebar";
import { Separator } from "@/components/ui/separator";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const { userName, isAuthenticated } = useAuthStore();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    if (mounted && !isAuthenticated()) {
      router.push("/login");
    }
  }, [mounted, isAuthenticated, router]);

  // Render nothing until client hydration completes (avoids server/client mismatch)
  if (!mounted) return null;
  if (!isAuthenticated()) return null;

  return (
    <SidebarProvider>
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:z-50 focus:top-2 focus:left-2 focus:rounded-md focus:bg-primary focus:px-4 focus:py-2 focus:text-primary-foreground focus:text-sm"
      >
        Skip to main content
      </a>
      <DashboardSidebar userName={userName} />
      <SidebarInset>
        <header className="flex h-14 items-center gap-2 border-b px-4" role="banner">
          <SidebarTrigger aria-label="Toggle sidebar navigation" />
          <Separator orientation="vertical" className="h-6" aria-hidden="true" />
          <span className="text-sm text-muted-foreground">
            Immigration Empowerment through Data Portability
          </span>
        </header>
        <main id="main-content" className="flex-1 p-4 sm:p-6">{children}</main>
      </SidebarInset>
    </SidebarProvider>
  );
}
