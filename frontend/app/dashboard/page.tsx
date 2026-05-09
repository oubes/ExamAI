"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarInset,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarProvider,
  SidebarRail,
  useSidebar,
} from "@/components/ui/sidebar";

import {
  ClipboardCheck,
  MessageSquareText,
  BarChart3,
  Sparkles,
  Search,
  BookOpen,
  Trophy,
  History,
  GraduationCap,
  Lightbulb,
  Zap,
  LayoutDashboard,
  LogOut
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { TooltipProvider } from "@/components/ui/tooltip";

import { meService, MeResponse } from "@/services/dashboard.service";
import { authService } from "@/services/auth.service";

// ---- Navigation Config ----
const studentNav = [
  { title: "Dashboard", icon: LayoutDashboard, href: "/dashboard" },
  { title: "My Subjects", icon: BookOpen, href: "/subjects" },
  { title: "My Exams", icon: ClipboardCheck, href: "/student/exams" },
  { title: "Feedback", icon: MessageSquareText, href: "/student/feedback" },
  { title: "Learning Gaps", icon: Lightbulb, href: "/student/gaps" },
  { title: "Performance History", icon: History, href: "/student/history" },
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
          <span className="text-sm font-bold tracking-tight text-white uppercase">ExamAI Student</span>
          <span className="text-[10px] text-zinc-500 font-mono italic">System_Active</span>
        </div>
      </div>
    </SidebarHeader>
  );
}

// ---- Main Dashboard Component ----
export default function StudentDashboard() {
  const router = useRouter();
  const [user, setUser] = useState<MeResponse | null>(null);
  const [loading, setLoading] = useState(true);

  // ---- Auth Actions ----
  const handleLogout = async () => {
    try {
      await authService.logout();
      router.replace("/AuthPage");
    } catch (error) {
      console.error("Logout Fail", error);
      localStorage.clear();
      router.replace("/AuthPage");
    }
  };

  // ---- Guarded Data Fetching ----
  useEffect(() => {
    const checkAuthAndLoad = async () => {
      try {
        const userData = await meService.getMe();
        if (!userData) throw new Error("Unauthorized");
        setUser(userData);
        setLoading(false);
      } catch (error) {
        router.replace("/AuthPage");
      }
    };
    checkAuthAndLoad();
  }, [router]);

  // ---- Blocking UI State ----
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

  // ---- Final Render Block ----
  if (!user) return null;

  return (
    <TooltipProvider delayDuration={0}>
      <SidebarProvider>
        <div className="flex min-h-screen w-full bg-[#030303] text-zinc-100 antialiased">
          
          {/* Background FX */}
          <div className="fixed inset-0 pointer-events-none">
            <div className="absolute top-[-10%] left-[-5%] w-[40%] h-[40%] bg-blue-600/5 blur-[120px] rounded-full opacity-40" />
          </div>

          {/* Sidebar Section */}
          <Sidebar 
            variant="inset" 
            collapsible="icon" 
            className="border-none bg-zinc-950/50 overflow-x-hidden"
          >
            <SidebarHeaderTrigger />

            <SidebarContent className="overflow-x-hidden">
              <SidebarGroup>
                <SidebarGroupLabel className="px-4 text-[10px] font-bold uppercase tracking-[0.3em] text-zinc-600 group-data-[collapsible=icon]:hidden">
                  Academic Portal
                </SidebarGroupLabel>
                <SidebarGroupContent className="mt-4">
                  <SidebarMenu>
                    {studentNav.map((item) => (
                      <SidebarMenuItem key={item.title}>
                        <SidebarMenuButton
                          asChild
                          className="mx-2 h-11 rounded-lg text-zinc-400 hover:bg-white/5 hover:text-blue-400 transition-all group/item cursor-pointer"
                        >
                          <Link href={item.href}>
                            <item.icon className="h-4 w-4 transition-transform duration-200 group-hover/item:scale-125" />
                            <span className="font-medium">{item.title}</span>
                          </Link>
                        </SidebarMenuButton>
                      </SidebarMenuItem>
                    ))}
                  </SidebarMenu>
                </SidebarGroupContent>
              </SidebarGroup>
            </SidebarContent>

            <SidebarFooter className="p-3 space-y-2 transition-all duration-300">
              {/* Profile Box */}
              <Link 
                href="/student/profile" 
                className="flex items-center gap-3 rounded-xl bg-zinc-900/80 p-3 ring-1 ring-white/10 shadow-lg transition-all duration-200 hover:bg-zinc-800 hover:ring-blue-500/40 group/user active:scale-[0.98] group-data-[collapsible=icon]:p-0 group-data-[collapsible=icon]:h-10 group-data-[collapsible=icon]:w-10 group-data-[collapsible=icon]:mx-auto group-data-[collapsible=icon]:justify-center cursor-pointer"
              >
                <Avatar className="h-7 w-7 border border-blue-500/20 shrink-0 transition-transform group-hover/user:scale-110">
                  <AvatarFallback className="bg-zinc-800 text-[10px] font-bold text-blue-400">
                    {user?.full_name?.split(' ').map((n: string) => n[0]).join('').toUpperCase() || 'ST'}
                  </AvatarFallback>
                </Avatar>
                <div className="flex flex-col truncate group-data-[collapsible=icon]:hidden">
                  <span className="text-xs font-semibold text-zinc-100 group-hover/user:text-blue-400 transition-colors">{user?.full_name}</span>
                  <span className="text-[9px] text-zinc-500 truncate">{user?.email}</span>
                </div>
              </Link>

              {/* Logout Button */}
              <button 
                onClick={handleLogout}
                className="flex w-full items-center gap-3 rounded-xl px-4 py-3 text-zinc-500 hover:bg-red-500/10 hover:text-red-400 transition-all duration-200 group/logout active:scale-95 group-data-[collapsible=icon]:justify-center group-data-[collapsible=icon]:px-0 cursor-pointer"
              >
                <LogOut className="h-4 w-4 transition-all duration-200 group-hover/logout:-translate-x-1 group-data-[collapsible=icon]:group-hover/logout:translate-x-0 group-data-[collapsible=icon]:group-hover/logout:scale-125" />
                <span className="text-xs font-bold uppercase tracking-wider group-data-[collapsible=icon]:hidden">Logout</span>
              </button>
            </SidebarFooter>
            <SidebarRail />
          </Sidebar>

          {/* Main Dashboard Inset */}
          <SidebarInset className="flex flex-col bg-transparent overflow-x-hidden">
            <header className="flex h-16 shrink-0 items-center gap-2 px-8" />

            <main className="relative z-10 flex-1 px-8 py-4 lg:px-16">
              
              {/* Header Info */}
              <div className="mb-12 flex flex-col gap-8 lg:flex-row lg:items-end lg:justify-between">
                <div>
                  <div className="flex items-center gap-2 mb-2 group cursor-default">
                    <Trophy className="h-3 w-3 text-yellow-500 group-hover:animate-bounce" />
                    <span className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest">Status: {user?.is_active ? 'Verified' : 'Pending'}</span>
                  </div>
                  <h1 className="text-4xl font-black tracking-tighter text-white">Welcome, {user?.full_name?.split(' ')[0]}</h1>
                  <p className="mt-2 text-sm text-zinc-500 max-w-md">Your personalized AI-driven academic command center is ready.</p>
                </div>

                {/* Actions */}
                <div className="flex items-center gap-4">
                  <div className="relative group">
                    <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-zinc-600 group-focus-within:text-blue-400 group-focus-within:scale-110 transition-all" />
                    <Input
                      placeholder="Search my results..."
                      className="h-11 w-[260px] border-none bg-zinc-900 pl-10 text-sm ring-1 ring-white/5 focus-visible:ring-blue-500/40 focus-visible:bg-zinc-900/80 rounded-xl transition-all"
                    />
                  </div>
                  <Button className="h-11 bg-zinc-100 px-6 font-bold text-black hover:bg-white hover:shadow-[0_0_20px_rgba(255,255,255,0.15)] rounded-xl shadow-lg active:scale-95 transition-all cursor-pointer">
                    Start New Practice
                  </Button>
                </div>
              </div>

              {/* Analytics Grid */}
              <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
                <StudentMetricCard title="Account Role" value={user?.role || 'User'} icon={Zap} trend="System Access" />
                <StudentMetricCard title="Latest Score" value="--" icon={ClipboardCheck} trend="No recent exams" />
                <StudentMetricCard title="Improvement" value="0%" icon={BarChart3} trend="Performance delta" />
                <StudentMetricCard title="AI Feedback" value="0 New" icon={MessageSquareText} trend="Contextual logs" />
              </div>

              {/* Sections Container */}
              <div className="mt-10 grid gap-8 lg:grid-cols-2">
                <InsightBlock
                  title="AI Learning Insights"
                  icon={Sparkles}
                  items={["Complete your first exam to unlock AI insights."]}
                />
                <InsightBlock
                  title="Upcoming Milestones"
                  icon={BookOpen}
                  items={["System Onboarding", "Profile Verification"]}
                />
              </div>

              {/* Exam Logs Container */}
              <div className="mt-10 rounded-3xl bg-zinc-900/60 p-8 shadow-xl ring-1 ring-white/[0.05]">
                <div className="flex items-center justify-between mb-8">
                  <h3 className="text-xl font-bold text-white tracking-tight">Recent Exam Performance</h3>
                  <Button variant="ghost" className="text-xs text-blue-400 hover:bg-blue-500/10 hover:text-blue-300 transition-colors cursor-pointer">View Full History</Button>
                </div>
                <div className="space-y-4">
                  <div className="text-center py-10 text-zinc-600 text-xs font-mono italic">
                    NO_EXAM_LOGS_FOUND_IN_SYNC_FOR_{user?.user_name?.toUpperCase()}
                  </div>
                </div>
              </div>

              {/* System Footer */}
              <footer className="mt-20 flex items-center justify-between border-t border-white/5 pt-10 opacity-60">
                <div className="flex items-center gap-4 group cursor-default">
                  <span className="text-[11px] font-black text-white tracking-[0.2em] uppercase group-hover:text-blue-400 transition-colors">ExamAI</span>
                  <span className="text-[10px] font-mono text-zinc-500 italic">Core v2.0 | Session: {new Date().toLocaleDateString()}</span>
                </div>
                <Badge className="bg-zinc-800 text-zinc-400 border-none px-3 py-1 font-mono text-[9px] hover:bg-zinc-700 transition-colors cursor-help">LIVE_SYNC_OK</Badge>
              </footer>

            </main>
          </SidebarInset>
        </div>
      </SidebarProvider>
    </TooltipProvider>
  );
}

// ---- UI Components ----

function StudentMetricCard({ title, value, icon: Icon, trend }: any) {
  return (
    <div className="group relative overflow-hidden rounded-2xl bg-zinc-900/90 p-6 shadow-2xl ring-1 ring-white/[0.08] hover:ring-blue-500/30 transition-all duration-300 hover:-translate-y-1 cursor-default">
      <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 group-hover:scale-125 group-hover:-rotate-12 transition-all duration-500">
        <Icon className="h-12 w-12" />
      </div>
      <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-zinc-800 mb-6 border border-white/5 group-hover:bg-blue-600/10 group-hover:border-blue-500/20 transition-all">
        <Icon className="h-5 w-5 text-blue-400 group-hover:scale-110 transition-transform" />
      </div>
      <div>
        <h3 className="text-[10px] font-bold text-zinc-500 uppercase tracking-[0.2em] mb-1">{title}</h3>
        <p className="text-2xl font-black text-white group-hover:text-blue-50 group-hover:translate-x-1 transition-all">{value}</p>
        <p className="mt-1 text-[10px] text-zinc-500 font-medium">{trend}</p>
      </div>
    </div>
  );
}

function InsightBlock({ title, icon: Icon, items }: any) {
  return (
    <div className="group rounded-3xl bg-zinc-900/60 p-8 ring-1 ring-white/[0.05] shadow-xl backdrop-blur-md hover:ring-white/10 transition-all">
      <div className="flex items-center gap-4 mb-8">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-600/10 text-blue-400 group-hover:bg-blue-600 group-hover:text-white transition-all">
          <Icon className="h-5 w-5" />
        </div>
        <h3 className="text-xl font-bold text-white tracking-tight">{title}</h3>
      </div>
      <div className="space-y-3">
        {items.map((item: string, idx: number) => (
          <div key={idx} className="group/item flex items-start gap-4 p-4 rounded-2xl bg-zinc-800/40 hover:bg-zinc-800/80 transition-all cursor-default hover:translate-x-1">
            <div className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-blue-500 shadow-[0_0_10px_rgba(37,99,235,0.8)] group-hover/item:scale-150 transition-transform" />
            <span className="text-sm text-zinc-400 leading-relaxed group-hover/item:text-zinc-200 transition-colors">{item}</span>
          </div>
        ))}
      </div>
    </div>
  );
}