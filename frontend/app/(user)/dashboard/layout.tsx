"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { SidebarProvider, SidebarInset } from "@/components/ui/sidebar";
import { TooltipProvider } from "@/components/ui/tooltip";
import { AppSidebar } from "@/components/user/dashboard/app-sidebar";
import { meService, MeResponse } from "@/services/dashboard.service";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [user, setUser] = useState<MeResponse | null>(null);
  const [loading, setLoading] = useState(true);

  // ---- Auth Guard ----
  useEffect(() => {
    const checkAuth = async () => {
      try {
        const userData = await meService.getMe();
        if (!userData) throw new Error();
        setUser(userData);
        setLoading(false);
      } catch {
        router.replace("/AuthPage");
      }
    };
    checkAuth();
  }, [router]);

  if (loading) {
    return (
      <div className="fixed inset-0 z-[9999] flex items-center justify-center bg-[#030303]">
        <div className="flex flex-col items-center gap-4">
          <div className="h-8 w-8 animate-spin rounded-full border-2 border-blue-500 border-t-transparent" />
          <span className="text-[10px] font-mono text-zinc-500 tracking-[0.3em] uppercase">Authenticating_Access...</span>
        </div>
      </div>
    );
  }

  return (
    <TooltipProvider delayDuration={0}>
      <SidebarProvider>
        <div className="flex min-h-screen w-full bg-[#030303] text-zinc-100 antialiased">
          <div className="fixed inset-0 pointer-events-none">
            <div className="absolute top-[-10%] left-[-5%] w-[40%] h-[40%] bg-blue-600/5 blur-[120px] rounded-full opacity-40" />
          </div>
          <AppSidebar user={user} />
          <SidebarInset className="flex flex-col bg-transparent overflow-x-hidden">
            <header className="flex h-16 shrink-0 items-center gap-2 px-8" />
            {children}
          </SidebarInset>
        </div>
      </SidebarProvider>
    </TooltipProvider>
  );
}