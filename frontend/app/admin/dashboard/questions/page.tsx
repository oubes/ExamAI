"use client";

import { useState, useEffect, useMemo, useCallback } from "react";
import { 
    Loader2, Search, HelpCircle, Trash2, LayoutGrid, List, 
    MoreVertical, Tag, BarChart3, BookOpen, 
    AlertCircle, RefreshCw, FileText, CheckSquare, Layers,
    Maximize2, Edit3, Plus, X, Check, Brain, SlidersHorizontal
} from "lucide-react";

// ---- Services & Types ----
import { questionService, QuestionBundle, QuestionBundleUpdateRequest, QuestionOption } from "@/services/questions.service";
import { educationService as subjectService } from "@/services/subjects.service";
import { chapterService } from "@/services/chapter.service";
import { topicService } from "@/services/topic.service";

// ---- UI Components ----
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { 
    DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger 
} from "@/components/ui/dropdown-menu";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogDescription,
    DialogClose,
} from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Slider } from "@/components/ui/slider";

export default function QuestionsPage() {
    // ---- State ----
    const [bundles, setBundles] = useState<QuestionBundle[]>([]);
    const [subjectsMap, setSubjectsMap] = useState<Record<string, string>>({});
    const [chaptersMap, setChaptersMap] = useState<Record<string, string>>({});
    const [topicsMap, setTopicsMap] = useState<Record<string, string>>({});
    
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [searchQuery, setSearchQuery] = useState("");
    const [viewMode, setViewMode] = useState<"grid" | "list">("list");
    const [activeTab, setActiveTab] = useState<string>("mcq");
    const [difficultyRange, setDifficultyRange] = useState<[number, number]>([0, 5]);

    // ---- Orchestrated Data Fetching ----
    const fetchData = useCallback(async () => {
        try {
            setIsLoading(true);
            setError(null);

            const [qRes, sRes, cRes, tRes] = await Promise.all([
                questionService.listQuestions(),
                subjectService.listSubjects(),
                chapterService.listChapters(),
                topicService.listTopics()
            ]);

            const sMap: Record<string, string> = {};
            sRes.items.forEach(s => sMap[s.id] = s.title);
            
            const cMap: Record<string, string> = {};
            cRes.items.forEach(c => cMap[c.id] = c.title);

            const tMap: Record<string, string> = {};
            tRes.items.forEach(t => tMap[t.id] = t.title);

            setBundles(Array.isArray(qRes) ? qRes : []);
            setSubjectsMap(sMap);
            setChaptersMap(cMap);
            setTopicsMap(tMap);

        } catch (err: any) {
            setError(err.message || "Protocol Failure: Neural link synchronization failed.");
        } finally {
            setIsLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchData();
    }, [fetchData]);

    const handleDelete = async (id: string) => {
        try {
            await questionService.deleteQuestion(id);
            setBundles(prev => prev.filter(b => b.question.id !== id));
        } catch (err: any) {
            console.error("Critical Failure:", err);
        }
    };

    const handleUpdate = (updatedBundle: QuestionBundle) => {
        setBundles(prev => prev.map(b => b.question.id === updatedBundle.question.id ? updatedBundle : b));
    };

    const filteredBundles = useMemo(() => {
        return bundles.filter(b => {
            const matchesSearch = b.question.content.toLowerCase().includes(searchQuery.toLowerCase());
            const matchesType = b.question.type === activeTab;
            const diff = b.question.difficulty || 0;
            const matchesDifficulty = diff >= difficultyRange[0] && diff <= difficultyRange[1];
            return matchesSearch && matchesType && matchesDifficulty;
        });
    }, [bundles, searchQuery, activeTab, difficultyRange]);

    return (
        <div className="flex flex-col min-h-screen bg-[#09090b] text-zinc-100 p-6 lg:p-10">
            
            <header className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 mb-10">
                <div>
                    <div className="flex items-center gap-2 mb-1">
                        <HelpCircle className="w-4 h-4 text-blue-500" />
                        <span className="text-xs font-mono uppercase tracking-tighter text-zinc-500">Knowledge</span>
                    </div>
                    <h1 className="text-3xl font-bold tracking-tight">Question Bank</h1>
                </div>

                <div className="flex items-center gap-3 w-full md:w-auto">
                    <div className="relative flex-1 md:w-80">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500 pointer-events-none" />
                        <Input 
                            placeholder="Query vectors..." 
                            className="bg-zinc-900 border-zinc-800 pl-10 focus:ring-blue-500/20 text-zinc-200"
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                        />
                    </div>
                    <Button className="bg-blue-600 hover:bg-blue-500 text-white gap-2 px-4 shadow-lg shadow-blue-500/10 cursor-pointer transition-all">
                        <Plus className="w-4 h-4" /> <span className="hidden sm:inline">Initialize Question</span>
                    </Button>
                </div>
            </header>
            <div className="flex flex-col xl:flex-row items-start xl:items-center justify-between mb-8 border-b border-zinc-800/50 pb-6 gap-6">
                <div className="flex flex-col md:flex-row items-start md:items-center gap-6 w-full xl:w-auto">
                    <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full md:w-auto">
                        <TabsList className="bg-zinc-900 border border-zinc-800 p-1 gap-1">
                            <TabsTrigger
                                value="mcq"
                                className="gap-2 cursor-pointer transition-colors data-[state=active]:bg-zinc-800 data-[state=active]:text-blue-400 hover:text-blue-400 hover:bg-blue-500/10 rounded-md p-2">
                                <div className="flex flex-col items-center leading-none">
                                    <CheckSquare className="w-3.5 h-3.5 mb-3" />
                                    <span>Multiple Choice</span>
                                </div>
                            </TabsTrigger>
                            <TabsTrigger
                                value="written"
                                className="gap-2 cursor-pointer transition-colors data-[state=active]:bg-zinc-800 data-[state=active]:text-purple-400 hover:text-blue-400 hover:bg-blue-500/10 rounded-md">
                                <div className="flex flex-col items-center leading-none">
                                    <FileText className="w-3.5 h-3.5 mb-3" />
                                    <span>Written Response</span>
                                </div>
                            </TabsTrigger>
                        </TabsList>
                    </Tabs>

                    <div className="flex flex-col gap-3 md:w-32 bg-zinc-900/50 border border-zinc-800/50 rounded-xl p-3">

                        {/* ---- Inputs ---- */}
                        <div className="flex items-center gap-2">

                            {/* Min */}
                            <div className="flex flex-col gap-1 flex-1 items-center">
                                <span className="text-[9px] font-mono text-zinc-500 uppercase">
                                    Min
                                </span>

                                <input
                                    type="text"
                                    min={1}
                                    max={difficultyRange[1]}
                                    value={difficultyRange[0]}
                                    onChange={(e) =>
                                        setDifficultyRange([Number(e.target.value), difficultyRange[1]])
                                    }
                                    className="
                                        w-full h-7 bg-zinc-950 border border-zinc-800 rounded-md
                                        text-center text-xs font-mono text-blue-400
                                        focus:outline-none focus:border-blue-500/50 transition-colors

                                        appearance-none
                                        [-moz-appearance:textfield]
                                    "
                                />
                            </div>

                            {/* Max */}
                            <div className="flex flex-col gap-1 flex-1 items-center">
                                <span className="text-[9px] font-mono text-zinc-500 uppercase">
                                    Max
                                </span>

                                <input
                                    type="text"
                                    min={difficultyRange[0]}
                                    max={10}
                                    value={difficultyRange[1]}
                                    onChange={(e) =>
                                        setDifficultyRange([difficultyRange[0], Number(e.target.value)])
                                    }
                                    className="
                                        w-full h-7 bg-zinc-950 border border-zinc-800 rounded-md
                                        text-center text-xs font-mono text-blue-400
                                        focus:outline-none focus:border-blue-500/50 transition-colors

                                        appearance-none
                                        [-moz-appearance:textfield]
                                    "
                                />
                            </div>

                        </div>
                    </div>
                </div>

                <div className="flex items-center gap-4 ml-auto xl:ml-0">
                    <div className="flex bg-zinc-900 border border-zinc-800 rounded-lg p-1">
                        <button
                            onClick={() => setViewMode("grid")}
                            className={`p-1.5 rounded-md transition-colors cursor-pointer ${
                                viewMode === "grid"
                                    ? "bg-zinc-800 text-white shadow-sm"
                                    : "text-zinc-500 hover:text-blue-400 hover:bg-blue-500/10"
                            }`}
                        >
                            <LayoutGrid className="w-4 h-4" />
                        </button>
                        <button
                            onClick={() => setViewMode("list")}
                            className={`p-1.5 rounded-md transition-colors cursor-pointer ${
                                viewMode === "list"
                                    ? "bg-zinc-800 text-white shadow-sm"
                                    : "text-zinc-500 hover:text-blue-400 hover:bg-blue-500/10"
                            }`}
                        >
                            <List className="w-4 h-4" />
                        </button>
                    </div>
                </div>
            </div>

            <main className="flex-1">
                {isLoading ? (
                    <div className="flex flex-col items-center justify-center h-64 gap-3">
                        <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />
                        <p className="text-zinc-500 text-sm font-mono uppercase tracking-widest">Hydrating Nodes</p>
                    </div>
                ) : error ? (
                    <div className="flex flex-col items-center justify-center h-64 border border-red-900/20 bg-red-500/5 rounded-2xl p-6">
                        <AlertCircle className="w-10 h-10 text-red-500 mb-4" />
                        <p className="text-zinc-500 text-sm font-mono mb-6">{error}</p>
                        <Button onClick={fetchData} variant="outline" className="border-zinc-800 hover:bg-zinc-800 gap-2 cursor-pointer">
                            <RefreshCw className="w-4 h-4" /> Re-sync
                        </Button>
                    </div>
                ) : filteredBundles.length === 0 ? (
                    <div className="flex flex-col items-center justify-center h-64 border-2 border-dashed border-zinc-800 rounded-2xl">
                        <p className="text-zinc-600 text-sm font-mono uppercase tracking-widest">Null Reference: No matching data</p>
                    </div>
                ) : (
                    <div className={viewMode === "grid" ? "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6" : "flex flex-col gap-4"}>
                        {filteredBundles.map((bundle) => (
                            <QuestionCard 
                                key={bundle.question.id} 
                                bundle={bundle} 
                                mode={viewMode}
                                subjectName={subjectsMap[bundle.question.subject_id] || "Subject Unknown"}
                                chapterName={chaptersMap[bundle.question.chapter_id] || "Chapter Unknown"}
                                topicName={topicsMap[bundle.question.topic_id] || "Topic Unknown"}
                                onDelete={() => handleDelete(bundle.question.id)}
                                onUpdate={handleUpdate}
                            />
                        ))}
                    </div>
                )}
            </main>
        </div>
    );
}

// ---- Sub-components ----

interface QuestionCardProps {
    bundle: QuestionBundle;
    mode: "grid" | "list";
    subjectName: string;
    chapterName: string;
    topicName: string;
    onDelete: () => void;
    onUpdate: (updated: QuestionBundle) => void;
}

function QuestionCard({ bundle, mode, subjectName, chapterName, topicName, onDelete, onUpdate }: QuestionCardProps) {
    const { question, options, model_answer } = bundle;
    const [isOverlayOpen, setIsOverlayOpen] = useState(false);
    const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
    
    const getDifficultyColor = (level: number) => {
        if (level <= 1) return "text-emerald-500 border-emerald-500/20";
        if (level === 2) return "!text-zinc-200 !border-zinc-200/30";
        return "text-red-400 border-red-500/20";
    };

    return (
        <>
            <div className={`group relative bg-zinc-900/40 border border-zinc-800/50 rounded-2xl transition-all duration-300 hover:border-zinc-700 ${mode === 'list' ? 'p-5' : 'p-6 flex flex-col h-full'}`}>
                <div className="relative flex justify-between items-start mb-4">
                    <div className="flex gap-2">
                        <Badge
                            variant="outline"
                            className={`bg-zinc-800/50 border-zinc-700 text-[10px] uppercase font-mono ${question.type === 'mcq' ? 'text-blue-400' : 'text-purple-400'}`}
                        >
                            {question.type}
                        </Badge>
                        <Badge
                            variant="outline"
                            className={`bg-zinc-800/50 text-[10px] font-mono flex gap-1 items-center transition-colors ${getDifficultyColor(question.difficulty || 0)}`}
                        >
                            <Brain className="w-2.5 h-2.5" /> 
                            Difficulty: {question.difficulty || 0}
                        </Badge>
                    </div>
                    <QuestionActions 
                        onDelete={onDelete} 
                        onEditClick={() => setIsEditDialogOpen(true)} 
                    />
                </div>

                <div className="relative flex-1">
                    <h3 className="text-zinc-200 font-medium leading-relaxed mb-4 line-clamp-3">
                        {question.content}
                    </h3>

                    <div className="flex flex-col gap-3 mb-6">
                        <div className="flex items-center gap-2 text-zinc-500">
                            <BookOpen className="w-3.5 h-3.5 text-blue-500/60" />
                            <span className="text-[11px] font-mono capitalize tracking-tighter text-zinc-300">
                                Subject: {subjectName}
                            </span>
                        </div>
                        <div className="flex items-center gap-2 text-zinc-500">
                            <Tag className="w-3.5 h-3.5 text-purple-500/60" />
                            <span className="text-[11px] font-mono capitalize tracking-tighter text-zinc-300">
                                Chapter: {chapterName}
                            </span>
                        </div>
                        <div className="flex items-center gap-2 text-zinc-500">
                            <Layers className="w-3.5 h-3.5 text-emerald-500/60" />
                            <span className="text-[11px] font-mono capitalize tracking-tighter text-zinc-300">
                                Topic: {topicName}
                            </span>
                        </div>
                    </div>

                    {question.type === "mcq" && (
                        <div className="space-y-2 mb-4">
                            {options.map((opt) => (
                                <div
                                    key={opt.id}
                                    className={`text-xs p-2.5 rounded-lg border transition-all ${opt.is_correct ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400' : 'bg-zinc-950/30 border-zinc-800/50 text-zinc-500'}`}
                                >
                                    {opt.option_text}
                                </div>
                            ))}
                        </div>
                    )}

                    {model_answer && (
                        <div 
                            onClick={() => setIsOverlayOpen(true)}
                            className="group/answer mt-4 p-3 bg-zinc-800/50 border border-zinc-800/50 hover:border-zinc-700 shadow-zinc-800/40 rounded-lg cursor-pointer transition-all relative overflow-hidden"
                        >
                            <div className="flex justify-between items-center mb-1">
                                <p className="text-[9px] uppercase font-bold text-zinc-600 tracking-[0.2em]">Standard Answer</p>
                                <Maximize2 className="w-3 h-3 text-zinc-700 group-hover/answer:text-zinc-400 transition-colors" />
                            </div>
                            <p className="text-xs text-zinc-400 italic line-clamp-2">
                                {model_answer.answer_text}
                            </p>
                        </div>
                    )}
                </div>

                <div className="relative mt-6 pt-4 border-t border-zinc-800/50 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <BarChart3 className="w-3 h-3 text-zinc-600" />
                        <span className="text-[11px] text-zinc-600 font-mono tracking-tighter">
                            Importance: {question.importance}
                        </span>
                    </div>
                </div>
            </div>

            <Dialog open={isOverlayOpen} onOpenChange={setIsOverlayOpen}>
                <DialogContent className="bg-zinc-950 border-zinc-800 text-zinc-100 max-w-2xl p-6">
                    <DialogHeader>
                        <DialogTitle className="hidden" />
                        <DialogDescription className="text-zinc-200 text-base leading-relaxed text-left font-medium border-b border-zinc-800 pb-4">
                            {question.content}
                        </DialogDescription>
                    </DialogHeader>
                    <div className="mt-4 p-6 bg-zinc-900/50 border border-zinc-800/50 rounded-2xl">
                        <p className="text-sm text-zinc-300 whitespace-pre-wrap leading-relaxed italic">
                            {model_answer?.answer_text}
                        </p>
                    </div>
                </DialogContent>
            </Dialog>

            <EditQuestionDialog 
                bundle={bundle} 
                isOpen={isEditDialogOpen} 
                onOpenChange={setIsEditDialogOpen} 
                onUpdate={onUpdate}
            />
        </>
    );
}

function EditQuestionDialog({ bundle, isOpen, onOpenChange, onUpdate }: { 
    bundle: QuestionBundle, 
    isOpen: boolean, 
    onOpenChange: (o: boolean) => void,
    onUpdate: (updated: QuestionBundle) => void
}) {
    const [isSaving, setIsSaving] = useState(false);
    const isMCQ = bundle.question.type === "mcq";

    const initializeOptions = useCallback(() => {
        if (!isMCQ) return [];
        const currentOptions = bundle.options || [];
        return Array.from({ length: 4 }).map((_, i) => {
            if (currentOptions[i]) {
                return { ...currentOptions[i] };
            }
            return { 
                id: `new-${i}`, 
                question_id: bundle.question.id,
                option_text: "", 
                is_correct: false, 
                order: i 
            } as QuestionOption;
        });
    }, [bundle, isMCQ]);

    const [formData, setFormData] = useState({
        content: bundle.question.content,
        importance: bundle.question.importance,
        difficulty: bundle.question.difficulty || 0,
        model_answer: bundle.model_answer?.answer_text || "",
        options: initializeOptions()
    });

    useEffect(() => {
        if (isOpen) {
            setFormData({
                content: bundle.question.content,
                importance: bundle.question.importance,
                difficulty: bundle.question.difficulty || 0,
                model_answer: bundle.model_answer?.answer_text || "",
                options: initializeOptions()
            });
        }
    }, [isOpen, bundle, initializeOptions]);

    const handleSave = async () => {
        try {
            setIsSaving(true);
            const payload: QuestionBundleUpdateRequest = {
                content: formData.content,
                importance: Number(formData.importance),
                difficulty: Number(formData.difficulty),
                model_answer: formData.model_answer,
                options: isMCQ ? formData.options : [],
            };

            const updated = await questionService.updateQuestion(bundle.question.id, payload);
            onUpdate(updated);
            onOpenChange(false);
        } catch (err) {
            console.error("Update Failure:", err);
        } finally {
            setIsSaving(false);
        }
    };

    const toggleCorrect = (index: number) => {
        setFormData(prev => ({
            ...prev,
            options: prev.options.map((opt, i) => ({
                ...opt,
                is_correct: i === index
            }))
        }));
    };

    return (
        <Dialog open={isOpen} onOpenChange={onOpenChange}>
            <DialogContent className="bg-zinc-950/85 backdrop-blur-xl border border-zinc-800 text-white sm:max-w-sm overflow-hidden rounded-2xl p-0 [&>button]:hidden shadow-2xl">
                <DialogClose asChild>
                    <button className="absolute right-4 top-4 z-50 p-1 text-zinc-500 hover:text-red-500 transition-colors cursor-pointer group">
                        <X className="h-5 w-5 group-hover:scale-110 transition-transform" />
                    </button>
                </DialogClose>

                <div className="absolute inset-0 bg-gradient-to-b from-blue-600/10 to-transparent pointer-events-none h-32" />

                <DialogHeader className="px-6 pt-8 pb-4 relative z-10">
                    <div className="flex items-center gap-3">
                        <div className="p-2 rounded-lg bg-blue-600/10 border border-blue-500/20">
                            <Edit3 className="h-5 w-5 text-blue-500" />
                        </div>
                        <DialogTitle className="text-xl font-black tracking-tight uppercase">Edit Question</DialogTitle>
                    </div>
                </DialogHeader>

                <div className="px-6 pb-6 space-y-5 relative z-10 max-h-[60vh] overflow-y-auto">
                    <div className="space-y-2">
                        <Label className="text-zinc-400 text-[10px] font-bold uppercase tracking-wider">Content</Label>
                        <Textarea
                            className="bg-zinc-900/30 border border-zinc-800 min-h-[80px] focus:ring-2 focus:ring-blue-600/40 rounded-xl transition-all resize-none text-sm"
                            value={formData.content}
                            onChange={(e) => setFormData(prev => ({ ...prev, content: e.target.value }))}
                        />
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                            <Label className="text-zinc-400 text-[10px] font-bold uppercase tracking-wider">Importance (1-10)</Label>
                            <Input
                                type="number"
                                className="bg-zinc-900/30 border border-zinc-800 h-10 rounded-xl focus:ring-2 focus:ring-blue-600/40 text-sm"
                                value={formData.importance}
                                onChange={(e) => setFormData(prev => ({ ...prev, importance: parseInt(e.target.value || "0") }))}
                            />
                        </div>

                        <div className="space-y-2">
                            <Label className="text-zinc-400 text-[10px] font-bold uppercase tracking-wider">Difficulty (0-5)</Label>
                            <Input
                                type="number"
                                className="bg-zinc-900/30 border border-zinc-800 h-10 rounded-xl focus:ring-2 focus:ring-amber-600/40 text-sm"
                                value={formData.difficulty}
                                onChange={(e) => setFormData(prev => ({ ...prev, difficulty: parseInt(e.target.value || "0") }))}
                            />
                        </div>
                    </div>

                    {isMCQ ? (
                        <div className="space-y-3">
                            <Label className="text-zinc-400 text-[10px] font-bold uppercase tracking-wider">Options & Correct Key</Label>
                            {formData.options.map((opt, index) => (
                                <div key={opt.id || index} className="flex items-center gap-2 group">
                                    <div className="relative flex-1">
                                        <span className="absolute left-3 top-1/2 -translate-y-1/2 text-[10px] font-bold text-zinc-600 group-focus-within:text-blue-500">
                                            {String.fromCharCode(65 + index)}
                                        </span>
                                        <Input
                                            className={`bg-zinc-900/30 border h-10 pl-8 rounded-xl focus:ring-2 focus:ring-blue-600/40 text-sm transition-all ${opt.is_correct ? 'border-emerald-500/50 bg-emerald-500/5' : 'border-zinc-800'}`}
                                            value={opt.option_text}
                                            onChange={(e) => {
                                                const newOptions = [...formData.options];
                                                newOptions[index].option_text = e.target.value;
                                                setFormData(prev => ({ ...prev, options: newOptions }));
                                            }}
                                        />
                                    </div>
                                    <button
                                        onClick={() => toggleCorrect(index)}
                                        className={`w-10 h-10 rounded-xl flex items-center justify-center border transition-all cursor-pointer ${opt.is_correct ? 'bg-emerald-600 border-emerald-500 text-white shadow-lg shadow-emerald-600/20' : 'bg-zinc-900 border-zinc-800 text-zinc-600 hover:border-zinc-700'}`}
                                    >
                                        <Check className={`w-4 h-4 ${opt.is_correct ? 'scale-110' : 'scale-100 opacity-20'}`} />
                                    </button>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <div className="space-y-2">
                            <Label className="text-zinc-400 text-[10px] font-bold uppercase tracking-wider">Standard Answer</Label>
                            <Textarea
                                className="bg-zinc-900/30 border border-zinc-800 min-h-[120px] focus:ring-2 focus:ring-purple-600/40 rounded-xl transition-all resize-none text-sm italic"
                                value={formData.model_answer}
                                onChange={(e) => setFormData(prev => ({ ...prev, model_answer: e.target.value }))}
                            />
                        </div>
                    )}
                </div>

                <div className="px-6 pb-8 flex gap-3 relative z-10 bg-zinc-950/50 pt-4 border-t border-zinc-900">
                    <Button
                        variant="ghost"
                        onClick={() => onOpenChange(false)}
                        className="flex-1 h-11 bg-zinc-900/50 hover:bg-red-600/20 hover:text-red-500 border border-zinc-800 rounded-xl font-bold transition-all cursor-pointer text-xs"
                    >
                        Cancel
                    </Button>
                    <Button
                        onClick={handleSave}
                        disabled={isSaving}
                        className="flex-1 h-11 bg-blue-600 hover:bg-blue-500 text-white font-bold rounded-xl shadow-lg shadow-blue-600/20 transition-all cursor-pointer text-xs"
                    >
                        {isSaving ? <Loader2 className="h-4 w-4 animate-spin" /> : "Commit Changes"}
                    </Button>
                </div>
            </DialogContent>
        </Dialog>
    );
}

function QuestionActions({ onDelete, onEditClick }: { onDelete: () => void, onEditClick: () => void }) {
    return (
        <DropdownMenu>
            <DropdownMenuTrigger asChild>
                <button className="p-1 hover:bg-zinc-800 rounded-md transition-colors text-zinc-500 cursor-pointer">
                    <MoreVertical className="w-4 h-4" />
                </button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="bg-zinc-950 border-zinc-800 text-zinc-300">
                <DropdownMenuItem 
                    onClick={onEditClick}
                    className="gap-4 cursor-pointer focus:bg-zinc-900 focus:text-white transition-colors h-10 hover:bg-blue-600/10 hover:text-white font-medium rounded-md"
                >
                    <Edit3 className="w-3.5 h-3.5" /> Edit
                </DropdownMenuItem>
                <DropdownMenuItem 
                    onClick={onDelete} 
                    className="gap-4 cursor-pointer text-red-500 focus:bg-red-500/10 focus:text-red-500 font-medium transition-colors h-10 hover:bg-red-500/10 hover:text-red-500"
                >
                    <Trash2 className="w-3.5 h-3.5" /> Delete
                </DropdownMenuItem>
            </DropdownMenuContent>
        </DropdownMenu>
    );
}