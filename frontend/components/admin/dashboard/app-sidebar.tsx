"use client";

import * as React from "react";
import Link from "next/link";
import { useRouter, usePathname } from "next/navigation";
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
  SidebarRail,
  useSidebar,
} from "@/components/ui/sidebar";
import {
  ClipboardCheck,
  MessageSquareText,
  BookOpen,
  GraduationCap,
  LayoutDashboard,
  LogOut
} from "lucide-react";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { authService } from "@/services/auth.service";
import { MeResponse } from "@/services/dashboard.service";

// ---- Navigation Config ----
const studentNav = [
  { title: "Dashboard", icon: LayoutDashboard, href: "/admin/dashboard", adminHref: "/admin/dashboard" },
  { title: "Subjects", icon: BookOpen, href: "/admin/dashboard/subjects" },
  { title: "Exams", icon: ClipboardCheck, href: "/admin/dashboard/exams" },
  { title: "Feedback", icon: MessageSquareText, href: "/admin/dashboard/feedback" },
];

// ---- Sidebar Header Component ----
function SidebarHeaderTrigger() {
  const { toggleSidebar } = useSidebar();
  return (
    <SidebarHeader className="px-4 py-8">
      <div className="flex items-center gap-3">
        <button 
          onClick={toggleSidebar}
          className="flex h-10 w-10 shrink-0 cursor-pointer items-center justify-center rounded-xl bg-zinc-800 ring-1 ring-white/10 shadow-2xl transition-all hover:bg-zinc-700 active:scale-95"
        >
          <GraduationCap className="h-5 w-5 text-blue-400" />
        </button>
        <div className="flex flex-col truncate group-data-[collapsible=icon]:hidden">
          <span className="text-sm font-bold tracking-tight text-white uppercase">ExamAI</span>
          <span className="text-[10px] text-zinc-500 font-mono italic">System_Active</span>
        </div>
      </div>
    </SidebarHeader>
  );
}

// ---- Main Sidebar Component ----
export function AppSidebar({ user }: { user: MeResponse | null }) {
  const router = useRouter();
  const pathname = usePathname();

  const handleLogout = async () => {
    try {
      await authService.logout();
      router.replace("/AuthPage");
    } catch (error) {
      localStorage.clear();
      router.replace("/AuthPage");
    }
  };

  return (
    <Sidebar variant="inset" collapsible="icon" className="border-none bg-zinc-950/50 overflow-x-hidden">
      <SidebarHeaderTrigger />
      <SidebarContent className="overflow-x-hidden">
        <SidebarGroup>
          <SidebarGroupLabel className="px-4 text-[10px] font-bold uppercase tracking-[0.3em] text-zinc-600 group-data-[collapsible=icon]:hidden">
            Academic Portal
          </SidebarGroupLabel>
          <SidebarGroupContent className="mt-4">
            <SidebarMenu>
              {studentNav.map((item) => {
                // ---- Logic to check if item is active (Standard or Admin path) ----
                const isActive = pathname === item.href || (item.adminHref && pathname === item.adminHref);

                return (
                  <SidebarMenuItem key={item.title}>
                    <SidebarMenuButton 
                      asChild 
                      isActive={isActive}
                      className={`mx-2 h-11 rounded-lg transition-all group/item cursor-pointer 
                        ${isActive 
                          ? "bg-blue-500/10 text-blue-400 ring-1 ring-blue-500/20" 
                          : "text-zinc-400 hover:bg-white/5 hover:text-blue-400"
                        }`}
                    >
                      <Link href={user?.role === "admin" && item.adminHref ? item.adminHref : item.href}>
                        <item.icon className={`h-4 w-4 transition-transform duration-200 
                          ${isActive ? "scale-110 text-blue-400" : "group-hover/item:scale-125"}`} 
                        />
                        <span className="font-medium">{item.title}</span>
                      </Link>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                );
              })}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      <SidebarFooter className="p-3 space-y-2 transition-all duration-300">
        <Link 
          href="/student/profile" 
          className={`flex items-center gap-3 rounded-xl p-3 ring-1 shadow-lg transition-all duration-200 group/user active:scale-[0.98] 
            group-data-[collapsible=icon]:p-0 group-data-[collapsible=icon]:h-10 group-data-[collapsible=icon]:w-10 group-data-[collapsible=icon]:mx-auto group-data-[collapsible=icon]:justify-center cursor-pointer
            ${pathname === "/student/profile" 
              ? "bg-blue-500/10 ring-blue-500/40 text-blue-400" 
              : "bg-zinc-900/80 ring-white/10 hover:bg-zinc-800 hover:ring-blue-500/40"
            }`}
        >
          <Avatar className="h-7 w-7 border border-blue-500/20 shrink-0 transition-transform group-hover/user:scale-110">
            <AvatarFallback className="bg-zinc-800 text-[10px] font-bold text-blue-400">
              {user?.full_name?.split(' ').map((n: string) => n[0]).join('').toUpperCase() || 'ST'}
            </AvatarFallback>
          </Avatar>
          <div className="flex flex-col truncate group-data-[collapsible=icon]:hidden">
            <span className={`text-xs font-semibold transition-colors ${pathname === "/student/profile" ? "text-blue-400" : "text-zinc-100 group-hover/user:text-blue-400"}`}>
              {user?.full_name}
            </span>
            <span className="text-[9px] text-zinc-500 truncate">{user?.email}</span>
          </div>
        </Link>

        <button onClick={handleLogout} className="flex w-full items-center gap-3 rounded-xl px-4 py-3 text-zinc-500 hover:bg-red-500/10 hover:text-red-400 transition-all duration-200 group/logout active:scale-95 group-data-[collapsible=icon]:justify-center group-data-[collapsible=icon]:px-0 cursor-pointer">
          <LogOut className="h-4 w-4 transition-all duration-200 group-hover/logout:-translate-x-1 group-data-[collapsible=icon]:group-hover/logout:translate-x-0 group-data-[collapsible=icon]:group-hover/logout:scale-125" />
          <span className="text-xs font-bold uppercase tracking-wider group-data-[collapsible=icon]:hidden">Logout</span>
        </button>
      </SidebarFooter>
      <SidebarRail />
    </Sidebar>
  );
}