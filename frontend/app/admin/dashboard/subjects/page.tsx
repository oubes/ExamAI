"use client";

import { useState, useCallback, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Loader2, Zap, Search } from "lucide-react";

// ---- UI Components ----
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { AddSubject } from "@/components/admin/dashboard/subjects/add-subject";
import { Subjects } from "@/components/admin/dashboard/subjects/subjects";

// ---- Services ----
import { educationService } from "@/services/subjects.service";
import { meService } from "@/services/dashboard.service";

import type { Subject, FilterStatus } from "@/components/admin/dashboard/subjects/types";

// ---- Logic Helpers ----
function filterSubjects(
    subjects: Subject[],
    filter: FilterStatus,
    search: string,
): Subject[] {
    return subjects.filter((subject) => {
        const searchLower = search.toLowerCase();
        const matchesSearch =
            subject.title.toLowerCase().includes(searchLower) ||
            subject.code.toLowerCase().includes(searchLower);

        if (!matchesSearch) return false;

        if (filter === "all") return true;
        if (filter === "active") return !subject.is_deleted;
        if (filter === "deleted") return subject.is_deleted;
        return false;
    });
}

export default function SubjectsPage() {
    const [subjects, setSubjects] = useState<Subject[]>([]);
    const [filter, setFilter] = useState<FilterStatus>("all");
    const [loading, setLoading] = useState(true);
    const [searchQuery, setSearchQuery] = useState("");

    const router = useRouter();

    // ---- Data Retrieval ----
    const fetchData = useCallback(async () => {
        try {
            const [userData, activeData, deletedData] = await Promise.all([
                meService.getMe(),
                educationService.listSubjects(),
                educationService.listDeletedSubjects(),
            ]);

            if (userData.role !== "admin") {
                router.replace("/dashboard");
                return;
            }

            const subjectsMap = new Map<string, Subject>();

            activeData.items.forEach((s: any) => {
                subjectsMap.set(s.id, { ...s, is_deleted: false });
            });

            deletedData.items.forEach((s: any) => {
                subjectsMap.set(s.id, { ...s, is_deleted: true });
            });

            const sortedSubjects = Array.from(subjectsMap.values()).sort((a, b) => {
                if (a.is_deleted === b.is_deleted) return 0;
                return a.is_deleted ? 1 : -1;
            });

            setSubjects(sortedSubjects);
        } catch (err) {
            router.replace("/login");
        } finally {
            setLoading(false);
        }
    }, [router]);

    useEffect(() => {
        fetchData();
    }, [fetchData]);

    // ---- Handlers ----
    function handleAdd(subject: Subject) {
        setSubjects((prev) => [subject, ...prev]);
        fetchData(); // Sync with server
    }

    function handleUpdate(subjectId: string, updated: Partial<Subject>) {
        setSubjects((prev) =>
            prev.map((subject) =>
                subject.id === subjectId ? { ...subject, ...updated } : subject,
            ),
        );
        fetchData(); // Sync with server
    }

    // ---- Fixed: Hard Delete Logic ----
    function handleRemove(subjectId: string) {
        // 1. Optimistic UI update (Immediate removal from DOM)
        setSubjects((prev) => prev.filter((s) => s.id !== subjectId));
        
        // 2. Refresh data from server to ensure sync
        fetchData();
    }

    if (loading && subjects.length === 0) {
        return (
            <div className="flex h-[80vh] items-center justify-center">
                <Loader2 className="h-6 w-6 animate-spin text-blue-600" />
            </div>
        );
    }

    return (
        <div className="relative z-10 w-full flex-1 px-4 py-8 lg:px-12">
            <div className="mb-12 flex flex-col gap-8 lg:flex-row lg:items-end lg:justify-between">
                <div>
                    <div className="flex items-center gap-2 mb-2">
                        <Zap className="h-3 w-3 text-blue-500" />
                        <span className="text-[10px] font-bold uppercase tracking-widest text-zinc-500">
                            System Admin
                        </span>
                    </div>
                    <h1 className="text-3xl font-bold tracking-tight">
                        Subjects
                    </h1>
                </div>

                <div className="flex flex-col md:flex-row items-center gap-4">
                    <Tabs
                        value={filter}
                        onValueChange={(v) => setFilter(v as FilterStatus)}
                        className="w-full md:w-auto"
                    >
                        <TabsList className="bg-zinc-900 border border-white/5 p-1 h-11 rounded-xl">
                            <TabsTrigger
                                value="all"
                                className="rounded-lg px-4 data-[state=active]:bg-zinc-700 data-[state=active]:text-white transition-all cursor-pointer"
                            >
                                All
                            </TabsTrigger>
                            <TabsTrigger
                                value="active"
                                className="rounded-lg px-4 data-[state=active]:bg-blue-600 data-[state=active]:text-white transition-all cursor-pointer"
                            >
                                Active
                            </TabsTrigger>
                            <TabsTrigger
                                value="deleted"
                                className="rounded-lg px-4 data-[state=active]:bg-red-900 data-[state=active]:text-white transition-all cursor-pointer"
                            >
                                Deleted
                            </TabsTrigger>
                        </TabsList>
                    </Tabs>

                    <div className="relative w-full lg:w-62.5">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-zinc-500" />
                        <Input
                            placeholder="Search Subject..."
                            className="h-11 pl-10 border-none bg-zinc-900 rounded-xl focus:ring-1 focus:ring-blue-500/50 transition-all text-white"
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                        />
                    </div>

                    <AddSubject onAdd={handleAdd} />
                </div>
            </div>

            <Subjects 
                subjects={filterSubjects(subjects, filter, searchQuery)}
                onUpdate={handleUpdate}
                onDelete={handleRemove} 
            />

            <footer className="mt-20 flex items-center justify-between border-t border-white/5 pt-8 opacity-40 w-full">
                <div className="flex items-center gap-4">
                    <span className="text-[10px] font-mono uppercase tracking-widest text-white">
                        ExamAI // Subjects
                    </span>
                    <div className="h-1 w-1 rounded-full bg-zinc-700" />
                    <span className="text-[10px] font-mono text-zinc-500">
                        200 OK
                    </span>
                </div>
                <Badge className="bg-zinc-800 text-zinc-400 border-none px-3 font-mono text-[9px]">
                    v2.8.2-PROD
                </Badge>
            </footer>
        </div>
    );
}