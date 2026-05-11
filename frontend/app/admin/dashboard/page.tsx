"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  Trophy,
  AlertTriangle,
  Search,
  Zap,
  ClipboardCheck,
  BarChart3,
  MessageSquareText,
  Sparkles,
  BookOpen,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { StudentMetricCard, InsightBlock } from "@/components/admin/dashboard/ui-cards";
import { meService, MeResponse } from "@/services/dashboard.service";

export default function AdminDashboardPage() {
  const [user, setUser] = useState<MeResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    // ---- Auth & Role Check ----
    meService
      .getMe()
      .then((data) => {
        setUser(data);
        if (data.role !== "admin") {
          router.replace("/dashboard");
        }
      })
      .catch((err) => {
        console.error("Auth error:", err);
        router.replace("/login");
      })
      .finally(() => setLoading(false));
  }, [router]);

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center bg-black">
        <div className="animate-pulse text-zinc-500 font-mono text-xs uppercase tracking-widest">
          Securing_Admin_Access...
        </div>
      </div>
    );
  }

  if (user?.role !== "admin") return null;

  const isVerified = user?.is_verified === true;
  const isLoaded = user !== null && !loading;

  return (
    <main className="relative z-10 flex-1 px-8 py-4 lg:px-16">
      {/* Header */}
      <div className="mb-12 flex flex-col gap-8 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <div className="flex items-center gap-2 mb-2 group cursor-default">
            {isLoaded &&
              (isVerified ? (
                <Trophy className="h-3 w-3 text-yellow-500 group-hover:animate-bounce" />
              ) : (
                <AlertTriangle className="h-3 w-3 text-red-800 group-hover:animate-pulse" />
              ))}

            <span
              className={`text-[10px] font-bold uppercase tracking-widest ${
                isVerified ? "text-zinc-500" : "text-red-800"
              }`}
            >
              {!isLoaded
                ? "Checking privileges..."
                : `Admin Status: ${isVerified ? "Verified" : "Unverified"}`}
            </span>
          </div>

          <h1 className="text-4xl font-black tracking-tighter text-white">
            Admin, {user?.full_name?.split(" ")[0]}
          </h1>

          <p className="mt-2 text-sm text-zinc-500 max-w-md">
            Elevated access active. System monitoring and user management enabled.
          </p>
        </div>

        {/* Search */}
        <div className="flex items-center gap-4">
          <div className="relative group">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-zinc-600 group-focus-within:text-blue-400" />
            <Input
              placeholder="Search users or logs..."
              className="h-11 w-[260px] border-none bg-zinc-900 pl-10 text-sm ring-1 ring-white/5 focus-visible:ring-blue-500/40 rounded-xl"
            />
          </div>

          <Button className="h-11 bg-red-600/10 border border-red-600/20 px-6 font-bold text-red-500 hover:bg-red-600/20 rounded-xl shadow-lg active:scale-95 transition-all">
            System Overhaul
          </Button>
        </div>
      </div>

      {/* Admin Grid */}
      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
        <StudentMetricCard
          title="System Role"
          value={user?.role || "Admin"}
          icon={Zap}
          trend="Superuser"
        />
        <StudentMetricCard title="Total Users" value="--" icon={ClipboardCheck} trend="Active sessions" />
        <StudentMetricCard title="System Health" value="100%" icon={BarChart3} trend="Node status" />
        <StudentMetricCard title="Pending Review" value="0" icon={MessageSquareText} trend="Queue empty" />
      </div>

      {/* Admin Insights */}
      <div className="mt-10 grid gap-8 lg:grid-cols-2">
        <InsightBlock
          title="Administrative Logs"
          icon={Sparkles}
          items={["All subsystems operational.", "No critical errors detected in the last 24h."]}
        />
        <InsightBlock
          title="Quick Actions"
          icon={BookOpen}
          items={["Manage User Permissions", "Audit Database Logs"]}
        />
      </div>

      {/* Footer */}
      <footer className="mt-20 flex items-center justify-between border-t border-white/5 pt-10 opacity-60">
        <div className="flex items-center gap-4 group cursor-default">
          <span className="text-[11px] font-black text-white tracking-[0.2em] uppercase group-hover:text-red-400 transition-colors">
            ExamAI Admin
          </span>
          <span className="text-[10px] font-mono text-zinc-500 italic">
            Core v2.0 | Admin Session
          </span>
        </div>

        <Badge className="bg-red-900/20 text-red-500 border-none px-3 py-1 font-mono text-[9px]">
          ADMIN_PRIVILEGES_ON
        </Badge>
      </footer>
    </main>
  );
}