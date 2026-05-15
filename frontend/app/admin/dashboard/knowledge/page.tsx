"use client";

import React, { useState, useEffect, useMemo } from "react";
import { 
  Loader2, Search, Trash2, 
  ChevronRight, Database, BarChart3, X, Cog, Edit3, Save, Play, AlertTriangle,
  Sparkles
} from "lucide-react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogDescription } from "@/components/ui/dialog";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import { Textarea } from "@/components/ui/textarea";

import { storageService, StorageFile } from "@/services/storage.service";
import { educationService, SubjectResponse } from "@/services/subjects.service";
import { knowledgeService } from "@/services/knowledge.service";

const GLOBAL_LIMIT = 1000;

export default function KnowledgeArchitecture() {
  const [files, setFiles] = useState<StorageFile[]>([]);
  const [subjects, setSubjects] = useState<SubjectResponse[]>([]);
  const [chunks, setChunks] = useState<any[]>([]);
  
  const [isLoading, setIsLoading] = useState(true);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isFetchingChunks, setIsFetchingChunks] = useState(false);
  const [isPipelineOpen, setIsPipelineOpen] = useState(false);
  const [selectedChunk, setSelectedChunk] = useState<any | null>(null);
  const [expandedGroups, setExpandedGroups] = useState<Record<string, boolean>>({});

  const [filterSubjectId, setFilterSubjectId] = useState<string>("all");
  const [searchQuery, setSearchQuery] = useState("");

  const [pipeFileId, setPipeFileId] = useState<string>("");
  const [pipeSubjectId, setPipeSubjectId] = useState<string>("");

  const [isEditing, setIsEditing] = useState(false);
  const [editContent, setEditContent] = useState("");
  const [isSaving, setIsSaving] = useState(false);

  const [isClusterPurgeOpen, setIsClusterPurgeOpen] = useState(false);
  const [targetGroupToPurge, setTargetGroupToPurge] = useState<{ docId: string; chunks: any[] } | null>(null);

  // ---- Section Name ----
  // Sync state registry assets on mount
  useEffect(() => {
    const bootstrap = async () => {
      try {
        const [f, s] = await Promise.all([
          storageService.listFiles(),
          educationService.listSubjects()
        ]);
        setFiles(f || []);
        setSubjects(s.items || []);
      } catch (e) {
        toast.error("Handshake Error: Failed to sync registry assets");
      } finally {
        setIsLoading(false);
      }
    };
    bootstrap();
  }, []);

  // ---- Section Name ----
  // Fetch vector chunks on filter mutation
  const loadKnowledge = async () => {
    if (filterSubjectId === "all") {
        setChunks([]);
        return;
    }
    try {
      setIsFetchingChunks(true);
      const res = await knowledgeService.listSubjectChunks(filterSubjectId, GLOBAL_LIMIT);
      setChunks(res.data || []);
    } catch (e: any) {
      toast.error(e.message || "Fragment Retrieval Failed");
    } finally {
      setIsFetchingChunks(false);
    }
  };

  useEffect(() => {
    loadKnowledge();
  }, [filterSubjectId]);

  // ---- Section Name ----
  // Run processing pipeline sequence
  const runPipeline = async () => {
    if (!pipeFileId || !pipeSubjectId) return;
    try {
      setIsProcessing(true);
      await knowledgeService.runKnowledgePipeline(pipeFileId, pipeSubjectId);
      toast.success("Pipeline Sequence Terminated Successfully");
      setIsPipelineOpen(false);
      if (filterSubjectId === pipeSubjectId) loadKnowledge();
    } catch (e: any) {
      toast.error(e.message);
    } finally {
      setIsProcessing(false);
    }
  };

  // ---- Section Name ----
  // Reprocess target document pipeline context
  const triggerClusterPipeline = async (e: React.MouseEvent, docId: string) => {
    e.stopPropagation();
    if (!filterSubjectId || filterSubjectId === "all" || !docId || docId === "unassigned") return;
    
    try {
      setIsProcessing(true);
      await knowledgeService.runKnowledgePipeline(docId, filterSubjectId);
      toast.success(`Re-processing sequence initiated for Document: ${docId}`);
      loadKnowledge();
    } catch (e: any) {
      toast.error(`Pipeline Trigger Failed: ${e.message}`);
    } finally {
      setIsProcessing(false);
    }
  };

  // ---- Section Name ----
  // Purge selected vector fragment
  const deleteFragment = async (e: React.MouseEvent, chunkId: string) => {
    e.stopPropagation();
    try {
      setChunks(prev => prev.filter(c => c.id !== chunkId));
      await knowledgeService.deleteChunk(chunkId);
      toast.success("Fragment purged from vector space");
    } catch (e: any) {
      loadKnowledge();
      toast.error("Purge failed: " + (e.message || "Backend rejection"));
    }
  };

  // ---- Section Name ----
  // Trigger overlay sequence for full cluster clear
  const triggerGroupPurgeOverlay = (e: React.MouseEvent, docId: string, groupChunks: any[]) => {
    e.stopPropagation();
    setTargetGroupToPurge({ docId, chunks: groupChunks });
    setIsClusterPurgeOpen(true);
  };

  // ---- Section Name ----
  // Purge entire cluster group context chunks asynchronously
  const executeClusterPurge = async () => {
    if (!targetGroupToPurge) return;
    const { docId, chunks: groupChunks } = targetGroupToPurge;

    try {
      setIsProcessing(true);
      setIsClusterPurgeOpen(false);
      setChunks(prev => prev.filter(c => c.document_id !== docId));
      await Promise.all(groupChunks.map(chunk => knowledgeService.deleteChunk(chunk.id)));
      toast.success("Entire document cluster purged from vector space");
    } catch (e: any) {
      loadKnowledge();
      toast.error("Cluster purge failed: " + (e.message || "Backend rejection"));
    } finally {
      setIsProcessing(false);
      setTargetGroupToPurge(null);
    }
  };

  // ---- Section Name ----
  // Sync manual payload modifications safely
  const updateFragment = async () => {
    if (!selectedChunk || !editContent.trim()) return;
    try {
      setIsSaving(true);
      
      const currentChunkId = selectedChunk.id;
      const targetContent = editContent.trim();
      const targetSubjectId = selectedChunk.subject_id || filterSubjectId;
      const targetDocId = selectedChunk.document_id;

      if (!targetSubjectId || targetSubjectId === "all" || !targetDocId) {
        throw new Error("Missing structural references: subject_id or document_id is unassigned");
      }
      
      await knowledgeService.updateChunk(currentChunkId, targetContent, targetSubjectId, targetDocId);
      
      setChunks(prev => prev.map(c => c.id === currentChunkId ? { ...c, content: targetContent } : c));
      setSelectedChunk((prev: any) => prev && prev.id === currentChunkId ? { ...prev, content: targetContent } : prev);
      
      toast.success("Vector content synchronized");
      setIsEditing(false);
    } catch (e: any) {
      console.error("Payload Sync Exception:", e);
      toast.error("Update failed: " + (e.response?.data?.message || e.message || "Internal Engine Rejection"));
    } finally {
      setIsSaving(false);
    }
  };

  // ---- Section Name ----
  // Compute optimized visual data structures
  const groupedData = useMemo(() => {
    let filtered = chunks;
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      filtered = filtered.filter(c => 
        c.content.toLowerCase().includes(q) ||
        c.keywords?.some((k: string) => k.toLowerCase().includes(q))
      );
    }

    const groups: Record<string, any[]> = {};
    filtered.forEach(chunk => {
      const docId = chunk.document_id || "unassigned";
      if (!groups[docId]) groups[docId] = [];
      groups[docId].push(chunk);
    });
    return groups;
  }, [chunks, searchQuery]);

  // ---- Section Name ----
  // Extract clean registry file metadata name
  const getFileName = (docId: string) => {
    if (docId === "unassigned") return "Unassigned Fragments";
    const file = files.find(f => f.id === docId);
    return file ? file.original_name : `Asset_ID: ${docId.slice(0, 8)}`;
  };

  // ---- Section Name ----
  // Toggle visibility layout of cluster node
  const toggleGroup = (docId: string) => {
    setExpandedGroups(prev => ({ ...prev, [docId]: !prev[docId] }));
  };

  if (isLoading) return (
    <div className="min-h-screen bg-[#020203] flex items-center justify-center font-mono">
      <div className="flex flex-col items-center gap-6">
        <Loader2 className="w-10 h-10 text-blue-600 animate-spin" />
        <span className="text-[9px] text-zinc-500 uppercase tracking-[0.8em]">Loading ...</span>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-[#020203] text-zinc-200 font-sans p-4 lg:p-8">
      <div className="max-w-6xl mx-auto space-y-8">
        
        {/* ---- Section Name ---- */}
        {/* View header management toolbar */}
        <header className="flex flex-col md:flex-row md:items-center justify-between gap-6 border-b border-zinc-900/50 pb-6">
          <div className="space-y-1">
            <h1 className="text-3xl font-black tracking-tighter uppercase italic leading-none">
              Knowledge <span className="text-blue-600">Base</span>
            </h1>
          </div>

            <Dialog open={isPipelineOpen} onOpenChange={setIsPipelineOpen}>
            <DialogTrigger asChild>
                <Button className="bg-blue-600 hover:bg-blue-500 text-white font-black h-12 px-8 rounded-xl transition-all duration-300 shadow-2xl shadow-blue-600/10 hover:shadow-blue-500/20 hover:scale-[1.02] active:scale-95 cursor-pointer border border-blue-500/20">
                <Cog className="w-5 h-5 mr-2 animate-spin-slow" />
                Chunking Knowledge
                </Button>
            </DialogTrigger>

            <DialogContent className="bg-[#050506] border border-zinc-800/80 text-white p-0 rounded-[2.2rem] max-w-lg overflow-hidden shadow-2xl shadow-black/60 [&>button]:hidden">

                {/* ---- Custom Close ---- */}
                <button
                onClick={() => setIsPipelineOpen(false)}
                className="absolute right-5 top-5 z-50 w-10 h-10 rounded-full bg-red-500/10 hover:bg-red-500 border border-red-500/20 hover:border-red-500 flex items-center justify-center transition-all duration-300 hover:scale-110 active:scale-95 shadow-lg shadow-red-500/10 hover:shadow-red-500/30 cursor-pointer group"
                >
                <X className="w-4 h-4 text-red-400 group-hover:text-white transition-colors duration-200" />
                </button>

                {/* ---- Header ---- */}
                <div className="relative px-7 pt-7 pb-5 border-b border-zinc-900 overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-br from-blue-600/10 via-transparent to-transparent pointer-events-none" />

                <DialogHeader className="relative space-y-2 text-left">
                    <DialogTitle className="text-2xl font-black tracking-tight">
                    Knowledge Chunking Pipeline
                    </DialogTitle>

                    <p className="text-sm text-zinc-500 font-medium leading-relaxed">
                    Configure target subject and target source book before initiating the chunking pipeline.
                    </p>
                </DialogHeader>
                </div>

                {/* ---- Body ---- */}
                <div className="p-7 space-y-6">

                {/* ---- Subject ---- */}
                <div className="w-full">
                    <label className="block mb-1 text-[10px] font-black uppercase tracking-[0.25em] text-zinc-500 ml-1">
                        Subject
                    </label>

                    <Select onValueChange={setPipeSubjectId} value={pipeSubjectId}>
                        <SelectTrigger className="w-full bg-zinc-900/70 border border-zinc-800 hover:border-blue-500/40 hover:bg-zinc-900 h-16 rounded-md text-sm transition-all duration-300 cursor-pointer px-5 py-5 shadow-lg shadow-black/20">
                            <SelectValue placeholder="Select target subject..." />
                        </SelectTrigger>

                        <SelectContent
                            position="popper"
                            sideOffset={8}
                            className="bg-[#09090B] border border-zinc-800 text-white rounded-md w-[var(--radix-select-trigger-width)] overflow-hidden shadow-2xl"
                        >
                            {subjects.map((s) => (
                                <SelectItem
                                    key={s.id}
                                    value={s.id}
                                    className="cursor-pointer focus:bg-zinc-600/50 focus:text-white rounded-lg p-3 transition-all duration-200"
                                >
                                    {s.title}
                                </SelectItem>
                            ))}
                        </SelectContent>
                    </Select>
                </div>

                {/* ---- File ---- */}
                <div className="w-full">
                    <label className="block mb-1 text-[10px] font-black uppercase tracking-[0.25em] text-zinc-500 ml-1">
                        Document
                    </label>

                    <Select onValueChange={setPipeFileId} value={pipeFileId}>
                        <SelectTrigger className="w-full bg-zinc-900/70 border border-zinc-800 hover:border-blue-500/40 hover:bg-zinc-900 h-16 rounded-md text-sm transition-all duration-300 cursor-pointer px-5 py-5 shadow-lg shadow-black/20">
                            <SelectValue placeholder="Select source file..." />
                        </SelectTrigger>

                        <SelectContent
                            position="popper"
                            sideOffset={8}
                            className="bg-[#09090B] border border-zinc-800 text-white rounded-md w-[var(--radix-select-trigger-width)] overflow-hidden shadow-2xl"
                        >
                            {files.map((f) => (
                                <SelectItem
                                    key={f.id}
                                    value={f.id}
                                    className="cursor-pointer focus:bg-zinc-600/50 focus:text-white rounded-lg p-3 transition-all duration-200"
                                >
                                    {f.original_name}
                                </SelectItem>
                            ))}
                        </SelectContent>
                    </Select>
                </div>

                {/* ---- Run Button ---- */}
                <Button
                    disabled={isProcessing || !pipeFileId || !pipeSubjectId}
                    onClick={runPipeline}
                    className="w-full h-14 rounded-2xl bg-blue-600 hover:bg-blue-500 disabled:bg-zinc-800 disabled:text-zinc-500 font-black tracking-wide transition-all duration-300 hover:scale-[1.01] active:scale-[0.985] shadow-xl shadow-blue-600/10 hover:shadow-blue-500/20 cursor-pointer"
                >
                    {isProcessing ? (
                    <div className="flex items-center gap-3">
                        <Loader2 className="w-5 h-5 animate-spin" />
                        <span>PROCESSING PIPELINE...</span>
                    </div>
                    ) : (
                    <div className="flex items-center gap-3">
                        <Sparkles className="w-5 h-5" />
                        <span>RUN PIPELINE</span>
                    </div>
                    )}
                </Button>
                </div>
            </DialogContent>
            </Dialog>

        </header>

        {/* ---- Section Name ---- */}
        {/* Primary engine controls metrics */}
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="relative flex-1 group">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-700 group-focus-within:text-blue-500 transition-colors" />
            <Input 
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Query content or keywords..." 
                className="bg-zinc-900/10 border-zinc-600/60 h-12 pl-12 rounded-2xl text-xs focus-visible:ring-blue-600/60 transition-all"
            />
          </div>
          <Select onValueChange={setFilterSubjectId} value={filterSubjectId}>
              <SelectTrigger 
                className="!h-[45px] w-full sm:w-[240px] !bg-zinc-950 !border-2 !border-zinc-700 hover:border-blue-500 rounded-2xl px-6 flex items-center justify-between cursor-pointer"
              >
                <div className="flex items-center gap-3">
                  <Database className="w-5 h-5 text-blue-500" />
                  <span className="text-[11px] font-black uppercase tracking-tighter text-zinc-200">
                      <SelectValue placeholder="Context Node" />
                  </span>
                </div>
              </SelectTrigger>
              
              <SelectContent 
                  position="popper" 
                  sideOffset={5} 
                  className="!min-w-[var(--radix-select-trigger-width)] !bg-zinc-950 !border-2 !border-zinc-700 !rounded-2xl !shadow-[0_20px_50px_rgba(0,0,0,0.5)]"
              >
                  <div className="p-1">
                  <SelectItem 
                      value="all" 
                      className="cursor-pointer !h-[50px] !text-[10px] font-bold uppercase text-zinc-500 focus:!bg-zinc-900 focus:!text-white rounded-xl mb-1"
                  >
                      Unselected
                  </SelectItem>
                  {subjects.map((s: { id: string; title: string }) => (
                      <SelectItem 
                      key={s.id} 
                      value={s.id} 
                      className="cursor-pointer !h-[50px] !text-[11px] font-semibold text-zinc-200 focus:!bg-blue-600 focus:!text-white rounded-xl"
                      >
                      {s.title}
                      </SelectItem>
                  ))}
                  </div>
              </SelectContent>
          </Select>
        </div>

        {/* ---- Section Name ---- */}
        {/* Dynamic multi cluster views */}
        {isFetchingChunks ? (
          <div className="py-32 flex flex-col items-center justify-center gap-6">
            <Loader2 className="w-8 h-8 text-blue-600 animate-spin" />
            <p className="text-[9px] font-mono text-zinc-700 uppercase tracking-[0.6em]">Rebuilding Cluster Data...</p>
          </div>
        ) : (
          <div className="grid gap-4">
            {Object.entries(groupedData).map(([docId, groupChunks]) => (
              <Collapsible 
                key={docId} 
                open={expandedGroups[docId]} 
                onOpenChange={() => toggleGroup(docId)}
                className="group/cluster"
              >
                <div className={`rounded-[1.5rem] border transition-all duration-300 ${expandedGroups[docId] ? 'bg-zinc-900/70 border-zinc-400/30 hover:border-zinc-400/60 shadow-xl' : 'bg-zinc-900/70 hover:bg-zinc-900/90 border-zinc-400/30 hover:border-zinc-400/60'}`}>
                  
                  <CollapsibleTrigger asChild>
                    <div className="p-5 md:p-6 flex items-center gap-6 cursor-pointer select-none">
                      <div className={`p-2.5 rounded-lg border transition-all duration-500 ${expandedGroups[docId] ? 'bg-blue-600 border-blue-500 text-white rotate-90' : 'bg-zinc-950 border-zinc-900 text-zinc-700'}`}>
                        <ChevronRight className="w-4 h-4" />
                      </div>
                      
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <Badge className="bg-zinc-900 text-zinc-500 border-zinc-500/40 text-[10px] font-black tracking-widest rounded px-1.5 py-0">Doc Name</Badge>
                          <div className="text-[12px] font-mono text-zinc-300">{getFileName(docId)}</div>
                        </div>
                        <h3 className="text-base font-black text-zinc-300 tracking-tight truncate uppercase italic">{getFileName(docId)}</h3>
                      </div>

                      <div className="flex items-center gap-4 lg:gap-6 px-6 border-l border-zinc-900/80">
                         <Button
                            size="icon"
                            disabled={isProcessing || docId === "unassigned"}
                            onClick={(e) => triggerClusterPipeline(e, docId)}
                            className="cursor-pointer bg-zinc-950 border border-zinc-800 hover:border-blue-500/50 hover:bg-blue-600/10 text-blue-500 h-10 w-10 rounded-xl transition-all active:scale-90 disabled:opacity-40 disabled:cursor-not-allowed"
                         >
                            {isProcessing ? <Loader2 className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4 fill-current" />}
                         </Button>

                         <Button
                            size="icon"
                            disabled={isProcessing}
                            onClick={(e) => triggerGroupPurgeOverlay(e, docId, groupChunks)}
                            className="cursor-pointer bg-zinc-950 border border-zinc-800 hover:border-red-500/50 hover:bg-red-600/10 text-red-500 h-10 w-10 rounded-xl transition-all active:scale-90 disabled:opacity-40 disabled:cursor-not-allowed"
                         >
                            <Trash2 className="w-4 h-4" />
                         </Button>

                         <div className="hidden lg:block text-center">
                            <p className="text-[8px] font-black text-zinc-500 uppercase">Chunks</p>
                            <p className="text-lg font-mono font-black text-zinc-500">{groupChunks.length}</p>
                         </div>
                         <div className="hidden lg:block text-center">
                            <p className="text-[8px] font-black text-zinc-500 uppercase">Mean Quality</p>
                            <p className="text-lg font-mono font-black text-blue-500/90">
                              {(groupChunks.reduce((acc, curr) => acc + (curr.quality_score || 0), 0) / groupChunks.length).toFixed(2)}
                            </p>
                         </div>
                      </div>
                    </div>
                  </CollapsibleTrigger>

                  <CollapsibleContent className="animate-in slide-in-from-top-4 duration-500 ease-out">
                    <div className="px-5 md:px-6 pb-6 space-y-2">
                      <div className="h-px bg-zinc-900/50 w-full mb-4" />
                      
                      {groupChunks.sort((a,b) => (a.chunk_index || 0) - (b.chunk_index || 0)).map((chunk) => (
                        <div 
                          key={chunk.id} 
                          onClick={() => {
                            setSelectedChunk(chunk);
                            setIsEditing(false);
                          }}
                          className="flex items-start gap-4 p-4 bg-zinc-950/40 border border-zinc-900/30 rounded-xl hover:border-blue-500/20 hover:bg-zinc-950 transition-all group/item relative overflow-hidden cursor-pointer"
                        >
                          <div className="mt-0.5">
                            <div className="w-8 h-8 rounded-lg bg-zinc-900 flex items-center justify-center border border-zinc-800/50 group-hover/item:border-blue-500/40 transition-all">
                              <span className="text-[10px] font-mono font-black text-zinc-700 group-hover/item:text-blue-500">
                                {String(chunk.chunk_index).padStart(2, '0')}
                              </span>
                            </div>
                          </div>
                          
                          <div className="flex-1 min-w-0 space-y-2">
                            <p className="text-[12px] leading-relaxed text-zinc-500 font-medium group-hover/item:text-zinc-300 transition-all line-clamp-2">
                              {chunk.content}
                            </p>
                            <div className="flex flex-wrap gap-1.5">
                               {chunk.keywords?.map((k: string, i: number) => (
                                 <Badge key={i} variant="secondary" className="bg-zinc-900/50 text-[8px] font-bold text-zinc-700 border-zinc-800/40 lowercase">#{k}</Badge>
                               ))}
                            </div>
                          </div>

                          <div className="flex flex-col items-center gap-2 opacity-0 group-hover/item:opacity-100 transition-all translate-x-2 group-hover/item:translate-x-0">
                             <Button 
                                size="icon" 
                                variant="ghost" 
                                onClick={(e) => deleteFragment(e, chunk.id)}
                                className="h-8 w-8 text-zinc-800 hover:text-red-500 hover:bg-red-500/10 rounded-lg cursor-pointer"
                             >
                                <Trash2 className="w-4 h-4" />
                             </Button>
                             
                             <Button 
                                size="icon" 
                                variant="ghost" 
                                onClick={(e) => {
                                  e.stopPropagation();
                                  setSelectedChunk(chunk);
                                  setEditContent(chunk.content);
                                  setIsEditing(true);
                                }}
                                className="h-8 w-8 text-zinc-800 hover:text-blue-500 hover:bg-blue-500/10 rounded-lg cursor-pointer"
                             >
                                <Edit3 className="w-3.5 h-3.5" />
                             </Button>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CollapsibleContent>
                </div>
              </Collapsible>
            ))}

            {Object.keys(groupedData).length === 0 && !isFetchingChunks && (
              <div className="py-40 flex flex-col items-center justify-center border border-zinc-900/20 border-dashed rounded-[3rem] bg-zinc-950/10">
                <BarChart3 className="w-12 h-12 text-zinc-800 mb-4" />
                <h3 className="text-lg font-black uppercase text-zinc-800 tracking-widest italic">Cluster Index Empty</h3>
              </div>
            )}
          </div>
        )}

        {/* ---- Section Name ---- */}
        {/* Interactive structural viewport overlay */}
        <Dialog 
          open={!!selectedChunk} 
          onOpenChange={(open) => {
            if (!open) {
              setSelectedChunk(null);
              setIsEditing(false);
            }
          }}
        >
          <DialogContent className="bg-zinc-950 ring-white/25 text-white p-0 min-w-md max-w-2xl overflow-hidden rounded-[2rem] shadow-2xl flex flex-col max-h-[90vh] [&>button]:hidden">
            
            <div className="sr-only">
              <DialogTitle>{isEditing ? "Modify Fragment Content" : "Vector Chunk Inspection"}</DialogTitle>
              <DialogDescription>Synchronizing manual overrides with the knowledge graph.</DialogDescription>
            </div>

            <div className="relative p-6 md:p-10 pt-8 flex flex-col flex-1 overflow-hidden">
              <button 
                onClick={() => {
                  setSelectedChunk(null);
                  setIsEditing(false);
                }}
                className="absolute top-6 right-6 p-2 rounded-xl hover:bg-zinc-900 transition-colors cursor-pointer group z-10"
              >
                <X className="w-5 h-5 text-zinc-700 group-hover:text-zinc-300" />
              </button>

              <div className="flex items-center gap-3 mb-4 shrink-0">
                 <div className="px-2 py-1 bg-blue-600/10 border border-blue-600/20 rounded-md">
                    <span className="text-[10px] font-black text-blue-500 uppercase tracking-tighter">Fragment #{selectedChunk?.chunk_index}</span>
                 </div>
                 <div className="h-px w-8 bg-zinc-800" />
                 <span className="text-[9px] font-mono text-zinc-700 uppercase tracking-[0.3em]">
                   {isEditing ? "Neural_Buffer_Edit" : "Vector_Deep_Scan"}
                 </span>
              </div>

              <div className="flex-1 overflow-hidden flex flex-col min-h-0">
                <div className="relative flex-1 overflow-y-auto mb-4 scrollbar-thin scrollbar-thumb-zinc-800 scrollbar-track-transparent">
                  <div className="absolute -left-4 top-0 bottom-0 w-1 bg-blue-600/30 rounded-full" />
                  
                  {isEditing ? (
                    <Textarea 
                      value={editContent}
                      onChange={(e) => setEditContent(e.target.value)}
                      className="w-full h-full min-h-[200px] bg-zinc-900/50 border border-zinc-800/50 text-zinc-200 rounded-2xl p-6 text-base leading-relaxed whitespace-pre-wrap resize-none transition-all placeholder:text-zinc-700 focus:outline-none focus:ring-0 focus-visible:ring-0 focus-visible:outline-none focus:border-blue-500 focus:bg-zinc-900/70"
                      placeholder="Input manual correction..."
                    />
                  ) : (
                    <Textarea 
                      readOnly
                      value={selectedChunk?.content || ""}
                      className="w-full h-full min-h-[200px] bg-zinc-900/50 border border-zinc-800/50 text-zinc-200 rounded-2xl p-6 text-base leading-relaxed whitespace-pre-wrap resize-none transition-all select-text cursor-default focus:outline-none focus:ring-0 focus-visible:ring-0 focus-visible:outline-none selection:bg-blue-600/30"
                    />
                  )}
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 shrink-0">
                  <div className="p-5 bg-zinc-900/60 hover:bg-zinc-900/90 border border-zinc-800/40 rounded-lg">
                    <p className="text-[9px] font-black text-zinc-600 uppercase tracking-widest">Extracted Keywords</p>
                    <div className="flex flex-wrap gap-2">
                      {selectedChunk?.keywords?.map((k: string, i: number) => (
                        <Badge key={i} variant="secondary" className="bg-zinc-800/30 text-[10px] border-zinc-700/50 lowercase text-zinc-400 py-1 px-2.5">
                          #{k}
                        </Badge>
                      ))}
                    </div>
                  </div>
                  <div className="p-5 bg-zinc-900/60 hover:bg-zinc-900/90 border border-zinc-800/40 rounded-lg flex flex-col justify-between">
                    <div>
                      <p className="text-[9px] font-black text-zinc-600 uppercase tracking-widest">Metadata Hash</p>
                      <div className="space-y-2">
                        <div className="flex justify-between items-center">
                          <span className="text-[10px] text-zinc-500">Quality Score</span>
                          <span className="text-xs font-mono font-bold text-emerald-500">{selectedChunk?.quality_score?.toFixed(2) || '0.00'}</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-[10px] text-zinc-500">Importance</span>
                          <span className="text-xs font-mono font-bold text-blue-500">{selectedChunk?.importance_score?.toFixed(2) || '0.00'}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* ---- Section Name ---- */}
            {/* Modal horizontal viewport alignments */}
            <div className="bg-zinc-900/20 border-t border-zinc-900/50 p-4 flex justify-center gap-3 shrink-0">
                {isEditing ? (
                  <>
                    <Button 
                      onClick={() => setIsEditing(false)} 
                      variant="ghost"
                      className="bg-zinc-900 hover:bg-red-500/20 text-zinc-500 hover:text-red-500/90 cursor-pointer rounded-xl h-10 text-[10px] font-black uppercase tracking-widest px-8 transition-colors"
                    >
                        Discard
                    </Button>
                    <Button 
                      disabled={isSaving}
                      onClick={updateFragment}
                      className="bg-blue-600 cursor-pointer hover:bg-blue-500 text-white rounded-xl h-10 text-[10px] font-black uppercase tracking-widest px-8 transition-all shadow-lg shadow-blue-600/20"
                    >
                        {isSaving ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : (
                          <>
                            <Save className="w-3.5 h-3.5 mr-2" />
                            Sync Changes
                          </>
                        )}
                    </Button>
                  </>
                ) : (
                  <>
                    <Button 
                      onClick={() => setSelectedChunk(null)} 
                      variant="ghost"
                      className="bg-zinc-900 hover:bg-red-500/20 text-zinc-500 hover:text-red-500/90 cursor-pointer rounded-xl h-10 text-[10px] font-black uppercase tracking-widest px-8 transition-colors"
                    >
                        Close
                    </Button>
                    <Button 
                      onClick={() => {
                        setEditContent(selectedChunk?.content || "");
                        setIsEditing(true);
                      }} 
                      className="bg-blue-600 cursor-pointer hover:bg-blue-500 text-white rounded-xl h-10 text-[10px] font-black uppercase tracking-widest px-8 transition-all shadow-lg shadow-blue-600/20"
                    >
                        <Edit3 className="w-3.5 h-3.5 mr-2" />
                        Edit Chunk
                    </Button>
                  </>
                )}
            </div>
          </DialogContent>
        </Dialog>

        {/* ---- Section Name ---- */}
        {/* Cluster Confirmation Action Overlay */}
        <Dialog open={isClusterPurgeOpen} onOpenChange={setIsClusterPurgeOpen}>
          <DialogContent className="bg-zinc-950 border-zinc-900 text-white p-6 rounded-[2rem] max-w-sm border-zinc-800/50">
            <DialogHeader className="flex flex-col items-center text-center space-y-3">
              <div className="w-12 h-12 rounded-full bg-red-500/10 flex items-center justify-center text-red-500 border border-red-500/20">
                <AlertTriangle className="w-6 h-6" />
              </div>
              <DialogTitle className="text-lg font-black uppercase tracking-tight italic text-red-500">
                Purge Document Cluster?
              </DialogTitle>
              <DialogDescription className="text-zinc-500 text-xs leading-relaxed">
                You are initiating a structural purge context. This sequence will wipe all{" "}
                <span className="text-white font-mono font-bold">
                  {targetGroupToPurge?.chunks.length}
                </span>{" "}
                chunks associated with{" "}
                <span className="text-white font-bold italic">
                  "{targetGroupToPurge ? getFileName(targetGroupToPurge.docId) : ""}"
                </span>{" "}
                permanently from the vector database.
              </DialogDescription>
            </DialogHeader>
            <div className="flex gap-3 mt-4">
              <Button
                variant="ghost"
                onClick={() => {
                  setIsClusterPurgeOpen(false);
                  setTargetGroupToPurge(null);
                }}
                className="cursor-pointer flex-1 bg-zinc-900 hover:bg-zinc-500/50 text-zinc-400 rounded-xl h-11 font-bold text-xs uppercase"
              >
                Abort
              </Button>
              <Button
                onClick={executeClusterPurge}
                className="cursor-pointer flex-1 bg-red-600/60 hover:bg-red-600/80 text-white rounded-xl h-11 font-black text-xs uppercase shadow-lg shadow-red-600/10"
              >
                Confirm Purge
              </Button>
            </div>
          </DialogContent>
        </Dialog>

      </div>
    </div>
  );
}