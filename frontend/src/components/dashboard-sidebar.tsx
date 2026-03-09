"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  useSidebar,
} from "@/components/ui/sidebar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import {
  Upload,
  BarChart3,
  Route,
  FileDown,
  Settings,
  LogOut,
  ChevronUp,
  LayoutDashboard,
  Moon,
  Sun,
} from "lucide-react";
import { useAuthStore } from "@/lib/store";
import { useTheme } from "@/components/theme-provider";

const navItems = [
  { title: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { title: "Evidence", href: "/dashboard/evidence", icon: Upload },
  { title: "Criteria", href: "/dashboard/criteria", icon: BarChart3 },
  { title: "Roadmap", href: "/dashboard/roadmap", icon: Route },
  { title: "Export", href: "/dashboard/export", icon: FileDown },
  { title: "Settings", href: "/dashboard/settings", icon: Settings },
];

export function DashboardSidebar({ userName }: { userName: string | null }) {
  const pathname = usePathname();
  const router = useRouter();
  const clearAuth = useAuthStore((s) => s.clearAuth);
  const { isMobile, setOpenMobile } = useSidebar();
  const { isDark, setTheme } = useTheme();

  const handleLogout = () => {
    clearAuth();
    router.push("/login");
  };

  const handleNavClick = () => {
    if (isMobile) {
      setOpenMobile(false);
    }
  };

  const initials = userName
    ? userName
        .split(" ")
        .map((n) => n[0])
        .join("")
        .toUpperCase()
        .slice(0, 2)
    : "U";

  return (
    <Sidebar aria-label="Dashboard navigation">
      <SidebarHeader>
        <div className="flex items-center gap-2.5 px-2 py-3">
          <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-violet-600 to-indigo-600 flex items-center justify-center" aria-hidden="true">
            <svg width="18" height="18" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M16 4 L18.5 13.5 L28 16 L18.5 18.5 L16 28 L13.5 18.5 L4 16 L13.5 13.5 Z" fill="white" opacity="0.95"/>
              <circle cx="16" cy="16" r="3" fill="white" opacity="0.3"/>
            </svg>
          </div>
          <span className="font-semibold text-base tracking-tight">Immigration Roadmap</span>
        </div>
      </SidebarHeader>
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>Navigation</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {navItems.map((item) => (
                <SidebarMenuItem key={item.href}>
                  <SidebarMenuButton
                    render={<Link href={item.href} onClick={handleNavClick} />}
                    isActive={pathname === item.href}
                  >
                    <item.icon className="h-4 w-4" />
                    <span>{item.title}</span>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
      <SidebarFooter>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton
              onClick={() => setTheme(isDark ? "light" : "dark")}
              aria-label={`Switch to ${isDark ? "light" : "dark"} mode`}
            >
              {isDark ? (
                <Sun className="h-4 w-4" aria-hidden="true" />
              ) : (
                <Moon className="h-4 w-4" aria-hidden="true" />
              )}
              <span>{isDark ? "Light Mode" : "Dark Mode"}</span>
            </SidebarMenuButton>
          </SidebarMenuItem>
          <SidebarMenuItem>
            <DropdownMenu>
              <DropdownMenuTrigger render={<SidebarMenuButton />}>
                <Avatar className="h-6 w-6">
                  <AvatarFallback className="text-xs bg-primary/10 text-primary">
                    {initials}
                  </AvatarFallback>
                </Avatar>
                <span className="truncate">{userName || "User"}</span>
                <ChevronUp className="ml-auto h-4 w-4" />
              </DropdownMenuTrigger>
              <DropdownMenuContent align="start" className="w-48">
                <DropdownMenuItem onClick={handleLogout}>
                  <LogOut className="h-4 w-4 mr-2" />
                  Log out
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarFooter>
    </Sidebar>
  );
}
