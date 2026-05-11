import { motion, AnimatePresence } from "framer-motion";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import {
    Zap,
    BookOpen,
    Activity,
    Archive,
    ChevronDown,
    Clock,
    Calendar,
} from "lucide-react";

import { ArchiveSubject } from "./archive-subject";
import { EditSubject } from "./edit-subject";
import { ActiveToggler } from "./active-toggler";
import { DeleteSubject } from "./delete-subject";
import { RestoreBtn } from "./restore-btn";

import type { Subject as TSubject } from "./types";

type SubjectProps = {
    subject: TSubject;
    onUpdate: (updated: Partial<TSubject>) => void;
    onDelete: () => void;
    expanded: boolean;
    onToggleExpand: () => void;
};

export function Subject({
    subject,
    onUpdate,
    onDelete,
    expanded,
    onToggleExpand,
}: SubjectProps) {
    const formatDate = (dateStr?: string) => {
        if (!dateStr) return "N/A";
        return new Date(dateStr).toLocaleDateString("en-US", {
            year: "numeric",
            month: "short",
            day: "numeric",
            hour: "2-digit",
            minute: "2-digit",
        });
    };

    return (
        <motion.div
            key={subject.id}
            layout
            initial={{ opacity: 0, scale: 0.98 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.98 }}
            className={`group overflow-hidden rounded-xl border transition-all duration-300 w-full shadow-sm ${
                subject.is_deleted
                    ? "border-red-900/20 bg-red-950/10 hover:bg-red-900/30 hover:border-red-900/50" 
                    : "border-white/10 bg-zinc-900/70 hover:bg-zinc-900/90"
            }`}
        >
            <div className="flex items-center justify-between px-5 h-16">
                <div className="flex items-center gap-4 flex-1 min-w-0 h-full">
                    <div
                        className={`h-9 w-9 rounded-lg flex items-center justify-center shrink-0 transition-all duration-300 ease-out group-hover:scale-105 ${
                            subject.is_deleted
                                ? "bg-red-500/10 text-red-500"
                                : "bg-blue-500/10 text-blue-500"
                        }`}
                    >
                        {subject.is_deleted ? (
                            <Archive className="h-4 w-4" />
                        ) : (
                            <BookOpen className="h-4 w-4" />
                        )}
                    </div>

                    <div className="min-w-0 flex-1">
                        <div className="flex items-center gap-2">
                            <h3 className="font-bold text-white text-sm truncate">
                                {subject.title}
                            </h3>
                            <Badge
                                variant="outline"
                                className={`text-[9px] font-mono shrink-0 h-5 px-1.5 transition-colors ${
                                    subject.is_deleted
                                        ? "border-red-900 text-red-400 group-hover:border-red-500"
                                        : "border-zinc-700 text-zinc-500"
                                }`}
                            >
                                {subject.code}
                            </Badge>
                        </div>
                    </div>
                </div>

                <div className="flex items-center gap-3 shrink-0 ml-4">
                    {!subject.is_deleted && (
                        <ActiveToggler
                            subjectId={subject.id}
                            active={subject.is_active}
                            onToggle={(newStatus) =>
                                onUpdate({
                                    is_active: newStatus,
                                })
                            }
                        />
                    )}

                    <div className="flex items-center gap-1.5">
                        {!subject.is_deleted && (
                            <EditSubject
                                subject={subject}
                                onEdit={(updated) => onUpdate(updated)}
                            />
                        )}

                        {subject.is_deleted ? (
                            <RestoreBtn
                                subjectId={subject.id}
                                onRestored={() =>
                                    onUpdate({ is_deleted: false })
                                }
                            />
                        ) : (
                            <ArchiveSubject
                                subjectId={subject.id}
                                subjectTitle={subject.title}
                                onArchived={() =>
                                    onUpdate({ is_deleted: true })
                                }
                            />
                        )}

                        <DeleteSubject
                            subjectId={subject.id}
                            subjectTitle={subject.title}
                            onDeleted={onDelete}
                        />
                    </div>

                    <div className="h-6 w-px bg-white/5" />

                    <Button
                        variant="ghost"
                        onClick={onToggleExpand}
                        className="h-8 w-8 p-0 rounded-full hover:bg-white/10 cursor-pointer transition-all active:scale-90"
                    >
                        <motion.div
                            animate={{
                                rotate: expanded ? 180 : 0,
                            }}
                            className="text-zinc-500 group-hover:text-white"
                        >
                            <ChevronDown className="h-4 w-4" />
                        </motion.div>
                    </Button>
                </div>
            </div>

            <AnimatePresence>
                {expanded && (
                    <motion.div
                        key={`desc-${subject.id}`}
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: "auto", opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{
                            duration: 0.3,
                            ease: "easeInOut",
                        }}
                        className="px-5 overflow-hidden"
                    >
                        <div className="pt-4 pb-6 border-t border-white/5 flex flex-col gap-6">
                            <div className="w-full">
                                <div className="flex items-center gap-2 mb-2">
                                    <Activity className="h-3 w-3 text-zinc-500" />
                                    <Label className="text-[9px] uppercase text-zinc-500 font-bold tracking-widest">
                                        Description
                                    </Label>
                                </div>
                                <p className="text-xs text-zinc-300 leading-relaxed whitespace-pre-wrap font-medium pl-5">
                                    {subject.description ||
                                        "No description provided."}
                                </p>
                            </div>

                            <div className="w-full flex flex-col sm:flex-row gap-6">
                                <div className="flex-1">
                                    <div className="flex items-center gap-2 mb-1.5">
                                        <Calendar className="h-3 w-3 text-zinc-500" />
                                        <Label className="text-[9px] uppercase text-zinc-500 font-bold tracking-widest">
                                            Created At
                                        </Label>
                                    </div>
                                    <p className="text-[11px] font-mono text-zinc-400 pl-5">
                                        {formatDate(subject.created_at)}
                                    </p>
                                </div>
                                <div className="flex-1">
                                    <div className="flex items-center gap-2 mb-1.5">
                                        <Clock className="h-3 w-3 text-zinc-500" />
                                        <Label className="text-[9px] uppercase text-zinc-500 font-bold tracking-widest">
                                            Last Updated
                                        </Label>
                                    </div>
                                    <p className="text-[11px] font-mono text-zinc-400 pl-5">
                                        {formatDate(subject.updated_at)}
                                    </p>
                                </div>
                            </div>

                            <div className="w-full">
                                <div className="flex items-center gap-2 mb-2">
                                    <Zap className="h-3 w-3 text-zinc-500" />
                                    <Label className="text-[9px] uppercase text-zinc-500 font-bold tracking-widest">
                                        System Status
                                    </Label>
                                </div>
                                <div className="flex flex-wrap gap-2 pl-5">
                                    <Badge
                                        className={`${
                                            subject.is_active
                                                ? "bg-blue-600/20 text-blue-400"
                                                : "bg-zinc-800 text-zinc-500"
                                        } border-none text-[9px]`}
                                    >
                                        {subject.is_active
                                            ? "ACTIVE SUBJECT"
                                            : "INACTIVE SUBJECT"}
                                    </Badge>
                                    <Badge
                                        className={`${
                                            subject.is_deleted
                                                ? "bg-red-600/20 text-red-400"
                                                : "bg-emerald-600/20 text-emerald-400"
                                        } border-none text-[9px]`}
                                    >
                                        {subject.is_deleted
                                            ? "STATUS DELETED"
                                            : "STATUS LIVE"}
                                    </Badge>
                                </div>
                            </div>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </motion.div>
    );
}