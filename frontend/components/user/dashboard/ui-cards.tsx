import { LucideIcon } from "lucide-react";

// ---- Metric Card ----
export function StudentMetricCard({ title, value, icon: Icon, trend }: any) {
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

// ---- Insight Block ----
export function InsightBlock({ title, icon: Icon, items }: any) {
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