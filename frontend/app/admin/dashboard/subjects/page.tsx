"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { 
  Plus, 
  BookOpen, 
  Loader2, 
  Zap,
  ShieldAlert,
  AlertTriangle,
  ChevronDown,
  Trash2,
  Archive,
  Search,
  RefreshCcw,
  Calendar,
  Clock,
  Activity,
  Power,
  X,
  Info,
  Pencil
} from "lucide-react";

// ---- UI Components ----
import { 
  Dialog, 
  DialogContent, 
  DialogHeader, 
  DialogTitle, 
  DialogTrigger,
  DialogClose
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Switch } from "@/components/ui/switch";

// ---- Services ----
import { educationService } from "@/services/subjects.service";
import { meService } from "@/services/dashboard.service";

// ---- Types ----
interface Subject {
  id: string;
  title: string;
  code: string;
  description: string;
  is_active: boolean;
  is_deleted?: boolean;
  created_at?: string;
  updated_at?: string;
}

type FilterStatus = "all" | "active" | "deleted";

export default function SubjectsPage() {
  const [activeSubjects, setActiveSubjects] = React.useState<Subject[]>([]);
  const [deletedSubjects, setDeletedSubjects] = React.useState<Subject[]>([]);
  const [loading, setLoading] = React.useState(true);
  const [submitting, setSubmitting] = React.useState(false);
  const [searchQuery, setSearchQuery] = React.useState("");
  const [isAddOpen, setIsAddOpen] = React.useState(false);
  const [editingSubject, setEditingSubject] = React.useState<Subject | null>(null);
  const [expandedId, setExpandedId] = React.useState<string | null>(null);
  const [filter, setFilter] = React.useState<FilterStatus>("all");
  const [newSubjectActive, setNewSubjectActive] = React.useState(true);
  
  const router = useRouter();

  // ---- Data Retrieval ----
  const fetchData = React.useCallback(async () => {
    try {
      setLoading(true);
      const [userData, activeData, deletedData] = await Promise.all([
        meService.getMe(),
        educationService.listSubjects(),
        educationService.listDeletedSubjects()
      ]);

      if (userData.role !== "admin") {
        router.replace("/dashboard");
        return;
      }

      setActiveSubjects(activeData.items.map((s: any) => ({ ...s, is_deleted: false })));
      setDeletedSubjects(deletedData.items.map((s: any) => ({ ...s, is_deleted: true })));
    } catch (err) {
      router.replace("/login");
    } finally {
      setLoading(false);
    }
  }, [router]);

  React.useEffect(() => { fetchData(); }, [fetchData]);

  // ---- Action Handlers ----
  const handleCreate = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setSubmitting(true);
    const formData = new FormData(e.currentTarget);
    
    const payload = {
      title: formData.get("title") as string,
      code: formData.get("code") as string,
      description: formData.get("description") as string,
      is_active: newSubjectActive
    };

    try {
      const res = await educationService.addSubject(payload);
      setActiveSubjects((prev) => [{...res, is_deleted: false}, ...prev]);
      setIsAddOpen(false);
      setNewSubjectActive(true);
    } catch (err) {
      console.error(err);
    } finally {
      setSubmitting(false);
    }
  };

  const handleUpdate = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!editingSubject) return;
    
    setSubmitting(true);
    const formData = new FormData(e.currentTarget);
    
    const payload = {
      title: formData.get("title") as string,
      code: formData.get("code") as string,
      description: formData.get("description") as string,
      is_active: newSubjectActive
    };

    try {
      const updated = await educationService.updateSubject(editingSubject.id, payload);
      setActiveSubjects(prev => prev.map(s => s.id === editingSubject.id ? { ...updated, is_deleted: false } : s));
      setEditingSubject(null);
    } catch (err) {
      console.error(err);
    } finally {
      setSubmitting(false);
    }
  };

  const handleToggleActive = async (id: string, currentStatus: boolean) => {
    try {
      const updated = await educationService.updateSubject(id, { is_active: !currentStatus });
      setActiveSubjects(prev => prev.map(s => s.id === id ? { ...s, is_active: updated.is_active } : s));
    } catch (err) {
      console.error(err);
    }
  };

  const handleRestore = async (id: string) => {
    try {
      const restored = await educationService.restoreSubject(id);
      setDeletedSubjects(prev => prev.filter(s => s.id !== id));
      setActiveSubjects(prev => [{...restored, is_deleted: false}, ...prev]);
    } catch (err) {
      console.error(err);
    }
  };

  const executeDelete = async (id: string, hard: boolean = false) => {
    try {
      if (hard) {
        await educationService.hardDeleteSubject(id);
        setDeletedSubjects(prev => prev.filter(s => s.id !== id));
        setActiveSubjects(prev => prev.filter(s => s.id !== id));
      } else {
        await educationService.deleteSubject(id);
        const subject = activeSubjects.find(s => s.id === id);
        if (subject) {
          setActiveSubjects(prev => prev.filter(s => s.id !== id));
          setDeletedSubjects(prev => [{...subject, is_deleted: true}, ...prev]);
        }
      }
    } catch (err) {
      console.error(err);
    }
  };

  const toggleExpand = (id: string) => {
    setExpandedId(expandedId === id ? null : id);
  };

  const getFilteredList = () => {
    let base = filter === "all" 
      ? [...activeSubjects, ...deletedSubjects] 
      : filter === "active" ? activeSubjects : deletedSubjects;

    return base.filter(s => 
      s.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      s.code.toLowerCase().includes(searchQuery.toLowerCase())
    );
  };

  const formatDate = (dateStr?: string) => {
    if (!dateStr) return "N/A";
    return new Date(dateStr).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit"
    });
  };

  if (loading) {
    return (
      <div className="flex h-[80vh] items-center justify-center">
        <Loader2 className="h-6 w-6 animate-spin text-blue-600" />
      </div>
    );
  }

  const subjects = getFilteredList();

  return (
    <div className="relative z-10 w-full flex-1 px-4 py-8 lg:px-12">
      
      {/* ---- Header Section ---- */}
      <div className="mb-12 flex flex-col gap-8 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <Zap className="h-3 w-3 text-blue-500" />
            <span className="text-[10px] font-bold uppercase tracking-widest text-zinc-500">System Admin</span>
          </div>
          <h1 className="text-4xl font-black tracking-tighter text-white uppercase">Subjects</h1>
        </div>

        <div className="flex flex-col md:flex-row items-center gap-4">
          <Tabs value={filter} onValueChange={(v) => setFilter(v as FilterStatus)} className="w-full md:w-auto">
            <TabsList className="bg-zinc-900 border border-white/5 p-1 h-11 rounded-xl">
              <TabsTrigger value="all" className="rounded-lg px-4 data-[state=active]:bg-zinc-700 data-[state=active]:text-white transition-all cursor-pointer">All</TabsTrigger>
              <TabsTrigger value="active" className="rounded-lg px-4 data-[state=active]:bg-blue-600 data-[state=active]:text-white transition-all cursor-pointer">Active</TabsTrigger>
              <TabsTrigger value="deleted" className="rounded-lg px-4 data-[state=active]:bg-red-900 data-[state=active]:text-white transition-all cursor-pointer">Deleted</TabsTrigger>
            </TabsList>
          </Tabs>

          <div className="relative w-full lg:w-[250px]">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-zinc-500" />
            <Input
              placeholder="Search Subject..."
              className="h-11 pl-10 border-none bg-zinc-900 rounded-xl focus:ring-1 focus:ring-blue-500/50 transition-all text-white"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>

          {/* ---- Add Subject Dialog ---- */}
          <Dialog open={isAddOpen} onOpenChange={(val) => {
            setIsAddOpen(val);
            if(val) setNewSubjectActive(true);
          }}>
            <DialogTrigger asChild>
              <Button className="h-11 bg-blue-600 px-6 font-bold hover:bg-blue-500 rounded-xl cursor-pointer active:scale-95 transition-all shadow-lg shadow-blue-600/20">
                <Plus className="mr-2 h-4 w-4" /> Add Subject
              </Button>
            </DialogTrigger>
            
            <DialogContent className="bg-zinc-950/85 backdrop-blur-xl border border-zinc-800 text-white sm:max-w-[500px] overflow-hidden rounded-2xl p-0 [&>button]:hidden shadow-2xl">
              <button 
                onClick={() => setIsAddOpen(false)}
                className="absolute right-4 top-4 z-50 p-1 text-zinc-500 hover:text-red-500 transition-colors cursor-pointer outline-none group"
              >
                <X className="h-5 w-5 group-hover:scale-110 transition-transform" />
              </button>

              <div className="absolute inset-0 bg-gradient-to-b from-blue-600/10 to-transparent pointer-events-none h-32" />
              
              <DialogHeader className="px-8 pt-8 pb-4 relative z-10">
                <div className="flex items-center gap-3 mb-1">
                  <div className="p-2 rounded-lg bg-blue-600/10 border border-blue-500/20">
                    <BookOpen className="h-5 w-5 text-blue-500" />
                  </div>
                  <div>
                    <DialogTitle className="text-2xl font-black tracking-tight uppercase">New Subject</DialogTitle>
                    <p className="text-xs text-zinc-500 font-medium">Register a new educational subject in the system</p>
                  </div>
                </div>
              </DialogHeader>

              <form onSubmit={handleCreate} className="px-8 pb-8 space-y-6 relative z-10">
                <div className="grid grid-cols-2 gap-4">
                  <div className="col-span-2 md:col-span-1 space-y-2">
                    <Label className="text-zinc-400 text-[10px] font-bold uppercase tracking-wider flex items-center gap-2">
                      <Activity className="h-3 w-3" /> Subject Title
                    </Label>
                    <Input 
                      name="title" 
                      placeholder="e.g. Mathematics"
                      className="bg-zinc-900/30 border-zinc-800 h-11 focus:ring-2 focus:ring-blue-600/40 rounded-xl transition-all cursor-text" 
                      required 
                    />
                  </div>

                  <div className="col-span-2 md:col-span-1 space-y-2">
                    <Label className="text-zinc-400 text-[10px] font-bold uppercase tracking-wider flex items-center gap-2">
                      <Zap className="h-3 w-3" /> Module Code
                    </Label>
                    <Input 
                      name="code" 
                      placeholder="MATH-101"
                      className="bg-zinc-900/30 border-zinc-800 h-11 focus:ring-2 focus:ring-blue-600/40 rounded-xl transition-all font-mono cursor-text" 
                      required 
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label className="text-zinc-400 text-[10px] font-bold uppercase tracking-wider">Detailed Description</Label>
                  <Textarea 
                    name="description" 
                    placeholder="Briefly describe the curriculum..."
                    className="bg-zinc-900/30 border-zinc-800 min-h-[100px] focus:ring-2 focus:ring-blue-600/40 rounded-xl transition-all resize-none cursor-text" 
                  />
                </div>

                <div className="flex items-center justify-between rounded-2xl bg-blue-600/5 p-4 border border-zinc-800 group transition-all hover:bg-blue-600/10">
                  <div className="flex gap-3 items-center">
                    <div className={`p-2 rounded-lg transition-colors ${newSubjectActive ? 'bg-blue-600 text-white' : 'bg-zinc-800 text-zinc-500'}`}>
                      <Power className="h-4 w-4" />
                    </div>
                    <div className="space-y-0.5">
                      <Label className="text-sm font-bold block">Initialize as Active</Label>
                      <p className="text-[10px] text-zinc-500">Live subjects are immediately visible</p>
                    </div>
                  </div>
                  <Switch 
                    checked={newSubjectActive} 
                    onCheckedChange={setNewSubjectActive}
                    className="data-[state=checked]:bg-blue-600 data-[state=unchecked]:bg-zinc-800 border-zinc-700 cursor-pointer"
                  />
                </div>

                <div className="flex gap-3 pt-2">
                  <DialogClose asChild>
                    <Button 
                      type="button" 
                      variant="ghost" 
                      className="flex-1 h-12 bg-zinc-900/50 hover:bg-red-600/20 hover:text-red-500 rounded-xl transition-all font-bold border border-zinc-800 cursor-pointer"
                    >
                      Discard
                    </Button>
                  </DialogClose>
                  <Button 
                    type="submit" 
                    disabled={submitting} 
                    className="flex-[2] h-12 bg-blue-600 hover:bg-blue-500 text-white font-bold rounded-xl shadow-lg shadow-blue-600/20 active:scale-[0.98] transition-all cursor-pointer"
                  >
                    {submitting ? (
                      <div className="flex items-center gap-2">
                        <Loader2 className="animate-spin h-4 w-4" />
                        <span>Deploying...</span>
                      </div>
                    ) : (
                      "Create Subject"
                    )}
                  </Button>
                </div>
              </form>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* ---- List Section ---- */}
      <motion.div className="flex flex-col gap-2 w-full">
        <AnimatePresence initial={false} mode="popLayout">
          {subjects.map((subject) => (
            <motion.div 
              key={subject.id}
              layout
              initial={{ opacity: 0, scale: 0.98 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.98 }}
              className={`group overflow-hidden rounded-xl border transition-colors w-full shadow-sm ${
                subject.is_deleted ? "border-red-900/20 bg-red-950/5 hover:bg-red-950/10" : "border-white/5 bg-zinc-900/70 hover:bg-zinc-900/90"
              }`}
            >
              <div className="flex items-center justify-between px-5 h-16">
                <div className="flex items-center gap-4 flex-1 min-w-0 h-full">
                  <div className={`h-9 w-9 rounded-lg flex items-center justify-center flex-shrink-0 transition-all duration-300 ease-out group-hover:scale-107 ${
                    subject.is_deleted ? "bg-red-500/10 text-red-500" : "bg-blue-500/10 text-blue-500"
                  }`}>
                    {subject.is_deleted ? <Archive className="h-4 w-4" /> : <BookOpen className="h-4 w-4" />}
                  </div>
                  
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2">
                      <h3 className="font-bold text-white text-sm truncate">{subject.title}</h3>
                      <Badge variant="outline" className={`text-[9px] font-mono flex-shrink-0 h-5 px-1.5 ${
                        subject.is_deleted ? "border-red-900 text-red-400" : "border-zinc-700 text-zinc-500"
                      }`}>{subject.code}</Badge>
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-3 flex-shrink-0 ml-4">
                  {!subject.is_deleted && (
                    <div className="flex items-center gap-2 mr-2">
                       <span className={`text-[9px] font-bold uppercase transition-colors ${subject.is_active ? 'text-blue-500' : 'text-zinc-600'}`}>
                        {subject.is_active ? 'Active' : 'Off'}
                      </span>
                      <Switch 
                        checked={subject.is_active} 
                        onCheckedChange={() => handleToggleActive(subject.id, subject.is_active)}
                        className="data-[state=checked]:bg-blue-600 data-[state=unchecked]:bg-zinc-800 border-zinc-700 scale-75 cursor-pointer"
                      />
                    </div>
                  )}

                  <div className="flex items-center gap-1.5">
                    {/* ---- Edit Action ---- */}
                    {!subject.is_deleted && (
                      <Button 
                        variant="ghost" 
                        onClick={() => {
                          setEditingSubject(subject);
                          setNewSubjectActive(subject.is_active);
                        }}
                        className="h-8 px-2 text-blue-500/60 hover:text-blue-400 hover:bg-blue-500/10 cursor-pointer flex gap-1.5 font-bold text-[9px] uppercase transition-all"
                      >
                        <Pencil className="h-3 w-3" /> Edit
                      </Button>
                    )}

                    {subject.is_deleted ? (
                      <Button 
                        variant="ghost" 
                        onClick={() => handleRestore(subject.id)}
                        className="h-8 px-2 text-emerald-500/60 hover:text-emerald-400 hover:bg-emerald-500/10 cursor-pointer flex gap-1.5 font-bold text-[9px] uppercase transition-all"
                      >
                        <RefreshCcw className="h-3 w-3" /> Restore
                      </Button>
                    ) : (
                      /* ---- Soft Delete Dialog ---- */
                      <Dialog>
                        <DialogTrigger asChild>
                          <Button 
                            variant="ghost" 
                            className="h-8 px-2 text-yellow-500/60 hover:text-yellow-400 hover:bg-yellow-500/10 cursor-pointer flex gap-1.5 font-bold text-[9px] uppercase transition-all"
                          >
                            <Trash2 className="h-3 w-3" /> Soft
                          </Button>
                        </DialogTrigger>
                        <DialogContent className="bg-zinc-950 border border-zinc-800 text-white shadow-2xl rounded-2xl p-6 [&>button]:hidden">
                          <DialogClose asChild>
                            <button className="absolute right-4 top-4 z-50 p-1 text-zinc-400 hover:text-yellow-500 transition-colors cursor-pointer outline-none group">
                              <X className="h-4 w-4" />
                            </button>
                          </DialogClose>
                          <DialogHeader>
                            <DialogTitle className="text-yellow-500 font-black flex items-center gap-2 uppercase tracking-tighter text-xl">
                              <Archive className="h-5 w-5" /> Archive Subject
                            </DialogTitle>
                          </DialogHeader>
                          <div className="py-6 space-y-3">
                            <p className="text-sm text-zinc-400 leading-relaxed">
                              Moving <span className="text-white font-bold">{subject.title}</span> to archives.
                            </p>
                            <div className="flex items-start gap-3 bg-yellow-500/5 border border-yellow-500/10 p-3 rounded-xl">
                               <Info className="h-4 w-4 text-yellow-500 flex-shrink-0 mt-0.5" />
                               <p className="text-[10px] text-yellow-500/80 leading-snug">The record will be hidden from live results but can be restored later from the 'Deleted' tab.</p>
                            </div>
                          </div>
                          <div className="flex gap-3">
                            <DialogClose asChild>
                              <Button variant="ghost" className="flex-1 bg-zinc-900 border border-zinc-800 cursor-pointer hover:bg-zinc-800 transition-colors font-bold rounded-xl h-11">Cancel</Button>
                            </DialogClose>
                            <Button onClick={() => executeDelete(subject.id, false)} className="flex-1 bg-yellow-600 hover:bg-yellow-500 text-white font-bold cursor-pointer transition-all rounded-xl h-11">Archive Subject</Button>
                          </div>
                        </DialogContent>
                      </Dialog>
                    )}

                    {/* ---- Hard Delete Dialog ---- */}
                    <Dialog>
                      <DialogTrigger asChild>
                        <Button 
                          variant="ghost" 
                          className="h-8 px-2 text-red-500/60 hover:text-red-400 hover:bg-red-500/10 cursor-pointer flex gap-1.5 font-bold text-[9px] uppercase transition-all"
                        >
                          <ShieldAlert className="h-3.5 w-3.5" /> Hard
                        </Button>
                      </DialogTrigger>
                      <DialogContent className="bg-zinc-950 border border-zinc-800 text-white shadow-2xl rounded-2xl p-6 [&>button]:hidden">
                        <DialogClose asChild>
                          <button className="absolute right-4 top-4 z-50 p-1 text-zinc-400 hover:text-red-500 transition-colors cursor-pointer outline-none group">
                            <X className="h-4 w-4" />
                          </button>
                        </DialogClose>
                        <DialogHeader>
                          <DialogTitle className="text-red-500 font-black flex items-center gap-2 uppercase tracking-tighter text-xl">
                            <AlertTriangle className="h-5 w-5" /> Critical Action
                          </DialogTitle>
                        </DialogHeader>
                        <div className="py-6 text-sm text-zinc-400 leading-relaxed">
                          You are about to <span className="text-white font-bold underline decoration-red-500/50 underline-offset-4">permanently destroy</span> the subject <span className="text-white font-bold">{subject.title}</span>. This data cannot be recovered.
                        </div>
                        <div className="flex gap-3">
                          <DialogClose asChild>
                            <Button variant="ghost" className="flex-1 bg-zinc-900 border border-zinc-800 cursor-pointer hover:bg-zinc-800 transition-colors font-bold rounded-xl h-11">Abort</Button>
                          </DialogClose>
                          <Button onClick={() => executeDelete(subject.id, true)} className="flex-1 bg-red-600 hover:bg-red-700 text-white font-bold cursor-pointer transition-all rounded-xl h-11">Confirm Purge</Button>
                        </div>
                      </DialogContent>
                    </Dialog>
                  </div>

                  <div className="h-6 w-[1px] bg-white/5" />

                  <Button
                    variant="ghost"
                    onClick={() => toggleExpand(subject.id)}
                    className="h-8 w-8 p-0 rounded-full hover:bg-white/10 cursor-pointer transition-all active:scale-90"
                  >
                    <motion.div animate={{ rotate: expandedId === subject.id ? 180 : 0 }} className="text-zinc-500 group-hover:text-white">
                      <ChevronDown className="h-4 w-4" />
                    </motion.div>
                  </Button>
                </div>
              </div>

              <AnimatePresence>
                {expandedId === subject.id && (
                  <motion.div
                    key={`desc-${subject.id}`}
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: "auto", opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.3, ease: "easeInOut" }}
                    className="px-5 overflow-hidden"
                  >
                    <div className="pt-4 pb-6 border-t border-white/5 flex flex-col gap-6">
                      <div className="w-full">
                        <div className="flex items-center gap-2 mb-2">
                          <Activity className="h-3 w-3 text-zinc-500" />
                          <Label className="text-[9px] uppercase text-zinc-500 font-bold tracking-widest">Description</Label>
                        </div>
                        <p className="text-xs text-zinc-300 leading-relaxed whitespace-pre-wrap font-medium pl-5">
                          {subject.description || "No description provided."}
                        </p>
                      </div>

                      <div className="w-full flex flex-col sm:flex-row gap-6">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1.5">
                            <Calendar className="h-3 w-3 text-zinc-500" />
                            <Label className="text-[9px] uppercase text-zinc-500 font-bold tracking-widest">Created At</Label>
                          </div>
                          <p className="text-[11px] font-mono text-zinc-400 pl-5">{formatDate(subject.created_at)}</p>
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1.5">
                            <Clock className="h-3 w-3 text-zinc-500" />
                            <Label className="text-[9px] uppercase text-zinc-500 font-bold tracking-widest">Last Updated</Label>
                          </div>
                          <p className="text-[11px] font-mono text-zinc-400 pl-5">{formatDate(subject.updated_at)}</p>
                        </div>
                      </div>

                      <div className="w-full">
                        <div className="flex items-center gap-2 mb-2">
                          <Zap className="h-3 w-3 text-zinc-500" />
                          <Label className="text-[9px] uppercase text-zinc-500 font-bold tracking-widest">System Status</Label>
                        </div>
                        <div className="flex flex-wrap gap-2 pl-5">
                          <Badge className={`${subject.is_active ? 'bg-blue-600/20 text-blue-400' : 'bg-zinc-800 text-zinc-500'} border-none text-[9px]`}>
                            {subject.is_active ? 'ACTIVE SUBJECT' : 'INACTIVE SUBJECT'}
                          </Badge>
                          <Badge className={`${subject.is_deleted ? 'bg-red-600/20 text-red-400' : 'bg-emerald-600/20 text-emerald-400'} border-none text-[9px]`}>
                            {subject.is_deleted ? 'STATUS DELETED' : 'STATUS LIVE'}
                          </Badge>
                        </div>
                      </div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          ))}
          {subjects.length === 0 && (
            <div className="py-20 text-center border-2 border-dashed border-white/5 rounded-3xl">
              <p className="text-zinc-500 font-mono text-sm uppercase tracking-widest">No matching records found</p>
            </div>
          )}
        </AnimatePresence>
      </motion.div>

      {/* ---- Edit Subject Dialog ---- */}
      <Dialog open={!!editingSubject} onOpenChange={(val) => !val && setEditingSubject(null)}>
        <DialogContent className="bg-zinc-950/85 backdrop-blur-xl border border-zinc-800 text-white sm:max-w-[500px] overflow-hidden rounded-2xl p-0 [&>button]:hidden shadow-2xl">
          <button 
            onClick={() => setEditingSubject(null)}
            className="absolute right-4 top-4 z-50 p-1 text-zinc-500 hover:text-red-500 transition-colors cursor-pointer outline-none group"
          >
            <X className="h-5 w-5 group-hover:scale-110 transition-transform" />
          </button>

          <div className="absolute inset-0 bg-gradient-to-b from-blue-600/10 to-transparent pointer-events-none h-32" />
          
          <DialogHeader className="px-8 pt-8 pb-4 relative z-10">
            <div className="flex items-center gap-3 mb-1">
              <div className="p-2 rounded-lg bg-blue-600/10 border border-blue-500/20">
                <Pencil className="h-5 w-5 text-blue-500" />
              </div>
              <div>
                <DialogTitle className="text-2xl font-black tracking-tight uppercase">Edit Subject</DialogTitle>
                <p className="text-xs text-zinc-500 font-medium">Update the properties of this educational subject</p>
              </div>
            </div>
          </DialogHeader>

          <form onSubmit={handleUpdate} className="px-8 pb-8 space-y-6 relative z-10">
            <div className="grid grid-cols-2 gap-4">
              <div className="col-span-2 md:col-span-1 space-y-2">
                <Label className="text-zinc-400 text-[10px] font-bold uppercase tracking-wider flex items-center gap-2">
                  <Activity className="h-3 w-3" /> Subject Title
                </Label>
                <Input 
                  name="title" 
                  defaultValue={editingSubject?.title}
                  placeholder="e.g. Mathematics"
                  className="bg-zinc-900/30 border-zinc-800 h-11 focus:ring-2 focus:ring-blue-600/40 rounded-xl transition-all cursor-text" 
                  required 
                />
              </div>

              <div className="col-span-2 md:col-span-1 space-y-2">
                <Label className="text-zinc-400 text-[10px] font-bold uppercase tracking-wider flex items-center gap-2">
                  <Zap className="h-3 w-3" /> Module Code
                </Label>
                <Input 
                  name="code" 
                  defaultValue={editingSubject?.code}
                  placeholder="MATH-101"
                  className="bg-zinc-900/30 border-zinc-800 h-11 focus:ring-2 focus:ring-blue-600/40 rounded-xl transition-all font-mono cursor-text" 
                  required 
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label className="text-zinc-400 text-[10px] font-bold uppercase tracking-wider">Detailed Description</Label>
              <Textarea 
                name="description" 
                defaultValue={editingSubject?.description}
                placeholder="Briefly describe the curriculum..."
                className="bg-zinc-900/30 border-zinc-800 min-h-[100px] focus:ring-2 focus:ring-blue-600/40 rounded-xl transition-all resize-none cursor-text" 
              />
            </div>

            <div className="flex items-center justify-between rounded-2xl bg-blue-600/5 p-4 border border-zinc-800 group transition-all hover:bg-blue-600/10">
              <div className="flex gap-3 items-center">
                <div className={`p-2 rounded-lg transition-colors ${newSubjectActive ? 'bg-blue-600 text-white' : 'bg-zinc-800 text-zinc-500'}`}>
                  <Power className="h-4 w-4" />
                </div>
                <div className="space-y-0.5">
                  <Label className="text-sm font-bold block">Status: {newSubjectActive ? 'Active' : 'Inactive'}</Label>
                  <p className="text-[10px] text-zinc-500">Toggle visibility of this subject</p>
                </div>
              </div>
              <Switch 
                checked={newSubjectActive} 
                onCheckedChange={setNewSubjectActive}
                className="data-[state=checked]:bg-blue-600 data-[state=unchecked]:bg-zinc-800 border-zinc-700 cursor-pointer"
              />
            </div>

            <div className="flex gap-3 pt-2">
              <Button 
                type="button" 
                variant="ghost" 
                onClick={() => setEditingSubject(null)}
                className="flex-1 h-12 bg-zinc-900/50 hover:bg-red-600/20 hover:text-red-500 rounded-xl transition-all font-bold border border-zinc-800 cursor-pointer"
              >
                Cancel
              </Button>
              <Button 
                type="submit" 
                disabled={submitting} 
                className="flex-[2] h-12 bg-blue-600 hover:bg-blue-500 text-white font-bold rounded-xl shadow-lg shadow-blue-600/20 active:scale-[0.98] transition-all cursor-pointer"
              >
                {submitting ? (
                  <div className="flex items-center gap-2">
                    <Loader2 className="animate-spin h-4 w-4" />
                    <span>Updating...</span>
                  </div>
                ) : (
                  "Update Subject"
                )}
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>

      {/* ---- Metadata Footer ---- */}
      <footer className="mt-20 flex items-center justify-between border-t border-white/5 pt-8 opacity-40 w-full">
        <div className="flex items-center gap-4">
          <span className="text-[10px] font-mono uppercase tracking-widest text-white">ExamAI // Subjects</span>
          <div className="h-1 w-1 rounded-full bg-zinc-700" />
          <span className="text-[10px] font-mono text-zinc-500">200 OK</span>
        </div>
        <Badge className="bg-zinc-800 text-zinc-400 border-none px-3 font-mono text-[9px]">v2.8.2-PROD</Badge>
      </footer>
    </div>
  );
}