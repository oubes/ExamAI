"use client";

import { AlertCircle, CheckCircle2, Sparkles } from "lucide-react";

// ---- Auth Logo Section ----
export const AuthLogo = ({ appName }: { appName: string }) => (
  <div className="flex flex-row items-center justify-center mb-8 gap-4 group cursor-default">
    <div className="relative flex h-12 w-12 items-center justify-center rounded-xl bg-zinc-900 border border-zinc-800 shadow-inner transition-all duration-500 group-hover:border-blue-500/50 group-hover:shadow-[0_0_20px_rgba(59,130,246,0.2)]">
      <Sparkles className="h-6 w-6 text-white relative z-10 transition-transform duration-500 group-hover:scale-110 group-hover:rotate-12" />
      <div className="absolute inset-0 rounded-xl bg-blue-500/0 group-hover:bg-blue-500/5 transition-colors duration-500" />
    </div>
    <div className="flex flex-col">
      <h1 className="text-3xl font-bold tracking-tight text-white leading-none transition-colors duration-500 group-hover:text-blue-50">
        {appName}
      </h1>
      <p className="text-[10px] text-zinc-600 mt-1 uppercase tracking-[0.2em] font-medium leading-none">
        Smart Learning Platform
      </p>
    </div>
  </div>
);

// ---- Status Messages ----
export const AuthStatusMessages = ({ error, success }: { error: string | null; success: string | null }) => (
  <>
    {error && (
      <div className="flex items-center gap-2 p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-xs animate-in fade-in slide-in-from-top-1">
        <AlertCircle className="h-4 w-4 shrink-0" />
        <p>{error}</p>
      </div>
    )}
    {success && (
      <div className="flex items-center gap-2 p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs animate-in fade-in slide-in-from-top-1">
        <CheckCircle2 className="h-4 w-4 shrink-0" />
        <p>{success}</p>
      </div>
    )}
  </>
);

// ---- Decorative Background ----
export const AuthBackground = () => (
  <div className="absolute inset-0 z-0">
    <div className="absolute inset-0 bg-gradient-to-tr from-blue-600/15 via-transparent to-indigo-600/15" />
    <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:44px_44px] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_50%,#000_70%,transparent_100%)]" />
  </div>
);