"use client";

import { useEffect, useState } from "react";
import { Trophy, Search, Zap, ClipboardCheck, BarChart3, MessageSquareText, Sparkles, BookOpen } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { StudentMetricCard, InsightBlock } from "@/components/dashboard/ui-cards";
import { meService, MeResponse } from "@/services/dashboard.service";

export default function DashboardPage() {
  const [user, setUser] = useState<MeResponse | null>(null);

  useEffect(() => {
    meService.getMe().then(setUser).catch(() => {});
  }, []);

  return (
    <main className="relative z-10 flex-1 px-8 py-4 lg:px-16">
      {/* Welcome Header */}
      <div className="mb-12 flex flex-col gap-8 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <div className="flex items-center gap-2 mb-2 group cursor-default">
            <Trophy className="h-3 w-3 text-yellow-500 group-hover:animate-bounce" />
            <span className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest">
              Status: {user?.is_active ? 'Verified' : 'Pending'}
            </span>
          </div>
          <h1 className="text-4xl font-black tracking-tighter text-white">
            Welcome, {user?.full_name?.split(' ')[0]}
          </h1>
          <p className="mt-2 text-sm text-zinc-500 max-w-md">Your personalized AI-driven academic command center is ready.</p>
        </div>

        <div className="flex items-center gap-4">
          <div className="relative group">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-zinc-600 group-focus-within:text-blue-400" />
            <Input placeholder="Search my results..." className="h-11 w-[260px] border-none bg-zinc-900 pl-10 text-sm ring-1 ring-white/5 focus-visible:ring-blue-500/40 rounded-xl" />
          </div>
          <Button className="h-11 bg-zinc-100 px-6 font-bold text-black hover:bg-white rounded-xl shadow-lg active:scale-95 transition-all">
            Start New Practice
          </Button>
        </div>
      </div>

      {/* Grid */}
      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
        <StudentMetricCard title="Account Role" value={user?.role || 'User'} icon={Zap} trend="System Access" />
        <StudentMetricCard title="Latest Score" value="--" icon={ClipboardCheck} trend="No recent exams" />
        <StudentMetricCard title="Improvement" value="0%" icon={BarChart3} trend="Performance delta" />
        <StudentMetricCard title="AI Feedback" value="0 New" icon={MessageSquareText} trend="Contextual logs" />
      </div>

      <div className="mt-10 grid gap-8 lg:grid-cols-2">
        <InsightBlock title="AI Learning Insights" icon={Sparkles} items={["Complete your first exam to unlock AI insights."]} />
        <InsightBlock title="Upcoming Milestones" icon={BookOpen} items={["System Onboarding", "Profile Verification"]} />
      </div>

      {/* Footer */}
      <footer className="mt-20 flex items-center justify-between border-t border-white/5 pt-10 opacity-60">
        <div className="flex items-center gap-4 group cursor-default">
          <span className="text-[11px] font-black text-white tracking-[0.2em] uppercase group-hover:text-blue-400 transition-colors">ExamAI</span>
          <span className="text-[10px] font-mono text-zinc-500 italic">Core v2.0 | Session: {new Date().toLocaleDateString()}</span>
        </div>
        <Badge className="bg-zinc-800 text-zinc-400 border-none px-3 py-1 font-mono text-[9px]">LIVE_SYNC_OK</Badge>
      </footer>
    </main>
  );
}