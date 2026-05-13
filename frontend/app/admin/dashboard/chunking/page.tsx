"use client";

import React, { useState, useEffect, useMemo } from "react";
import { 
  Loader2, Search, ChevronDown, ChevronRight, 
  Edit3, BookMarked, Cpu, X, AlertCircle, Plus, CloudUpload, Database
} from "lucide-react";
import { toast } from "sonner";

// ---- UI Components ----
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Textarea } from "@/components/ui/textarea";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

// ---- Services ----
import { storageService, StorageFile } from "@/services/storage.service";
import { questionService, ChunkResponse } from "@/services/chunk.service";
import { educationService, SubjectResponse } from "@/services/subjects.service";

export default function UnifiedStoragePage() {
  // ---- Section: State Management ----
  const [files, setFiles] = useState<StorageFile[]>([]);
  const [subjects, setSubjects] = useState<SubjectResponse[]>([]);
  const [allChunks, setAllChunks] = useState<ChunkResponse[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [expandedFiles, setExpandedFiles] = useState<Record<string, boolean>>({});
  
  // Pipeline State
  const [isPipelineModalOpen, setIsPipelineModalOpen] = useState(false);
  const [selectedFileId, setSelectedFileId] = useState<string>("");
  const [selectedSubjectId, setSelectedSubjectId] = useState<string>("");
  const [isProcessing, setIsProcessing] = useState(false);

  // Edit State
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [selectedChunk, setSelectedChunk] = useState<ChunkResponse | null>(null);
  const [editContent, setEditContent] = useState("");

  // ---- Section: Data Fetching ----
  const fetchInitialData = async () => {
    try {
      setIsLoading(true);
      const [filesData, subjectsData, chunksData] = await Promise.all([
        storageService.listFiles(),
        educationService.listSubjects(),
        questionService.listChunks()
      ]);
      setFiles(Array.isArray(filesData) ? filesData : []);
      setSubjects(subjectsData.items || []);
      setAllChunks(chunksData.items || []);
    } catch (error) {
      toast.error("Environment sync failed");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => { fetchInitialData(); }, []);

  // ---- Section: Logic & Filtering ----
  const processedFiles = useMemo(() => {
    const fileIdsWithChunks = new Set(allChunks.map(c => c.book_id));
    return files.filter(f => fileIdsWithChunks.has(f.id))
                .filter(f => f.original_name?.toLowerCase().includes(searchQuery.toLowerCase()));
  }, [files, allChunks, searchQuery]);

  const getChunksForFile = (fileId: string) => allChunks.filter(c => c.book_id === fileId);
  
  const getSubjectName = (subjectId: string) => {
    return subjects.find(s => s.id === subjectId)?.title || "Unknown Subject";
  };

  // ---- Section: Actions ----
  const executePipeline = async () => {
    if (!selectedFileId || !selectedSubjectId) return;
    try {
      setIsProcessing(true);
      await questionService.runSegmentationPipeline(selectedSubjectId, selectedFileId);
      toast.success("Pipeline executed successfully");
      setIsPipelineModalOpen(false);
      const chunksData = await questionService.listChunks();
      setAllChunks(chunksData.items || []);
    } catch (error) {
      toast.error("Pipeline failure");
    } finally {
      setIsProcessing(false);
    }
  };

  const handleUpdateChunk = async () => {
    if (!selectedChunk) return;
    try {
      setIsProcessing(true);
      await questionService.updateChunk(selectedChunk.id, { content: editContent });
      toast.success("Node updated");
      setIsEditModalOpen(false);
      setAllChunks(prev => prev.map(c => c.id === selectedChunk.id ? { ...c, content: editContent } : c));
    } catch (error) {
      toast.error("Update failed");
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#020203] text-zinc-100 p-6 lg:p-12 selection:bg-blue-500/30">
      <div className="max-w-6xl mx-auto">
        {/* ---- Section: Header ---- */}
        <header className="flex flex-col md:flex-row justify-between items-start md:items-end gap-6 mb-12">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <Cpu className="w-4 h-4 text-blue-500" />
              <span className="text-[10px] font-bold uppercase tracking-[0.2em] text-zinc-500">Knowledge Base</span>
            </div>
            <h1 className="text-4xl font-extrabold tracking-tight text-white lg:text-5xl">
              Segments<span className="text-blue-600">.</span>
            </h1>
          </div>

          <div className="flex items-center gap-3 w-full md:w-auto">
            <div className="relative flex-1 md:w-72">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
              <Input 
                placeholder="Search processed assets..." 
                className="bg-zinc-900/60 border-zinc-800 h-11 pl-10 rounded-xl focus:ring-1 focus:ring-blue-500/50"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
            <Button 
              onClick={() => setIsPipelineModalOpen(true)}
              className="bg-blue-600 hover:bg-blue-500 text-white h-11 px-5 rounded-xl font-bold text-xs transition-all shadow-lg shadow-blue-900/20 cursor-pointer"
            >
              <Plus className="w-4 h-4 mr-2" /> NEW PIPELINE
            </Button>
          </div>
        </header>

        {/* ---- Section: Main List ---- */}
        <div className="space-y-4">
          {isLoading ? (
            <div className="flex flex-col items-center justify-center py-20 gap-3">
              <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />
              <p className="text-zinc-600 text-[10px] font-mono uppercase tracking-widest">Loading Chunks...</p>
            </div>
          ) : processedFiles.length === 0 ? (
            <div className="text-center py-20 border-2 border-dashed border-zinc-900 rounded-3xl">
                <AlertCircle className="w-10 h-10 text-zinc-700 mx-auto mb-4" />
                <p className="text-zinc-500 text-sm">No processed chunks found.</p>
            </div>
          ) : (
            processedFiles.map((file) => {
              const fileChunks = getChunksForFile(file.id);
              const subjectName = getSubjectName(fileChunks[0]?.subject_id || "");

              return (
                <Collapsible key={file.id} open={expandedFiles[file.id]} onOpenChange={() => setExpandedFiles(prev => ({ ...prev, [file.id]: !prev[file.id] }))}>
                  <div className={`rounded-2xl border transition-all duration-200 ${expandedFiles[file.id] ? 'bg-zinc-900/90 border-zinc-700 shadow-xl' : 'bg-zinc-900/60 border-zinc-800/50 hover:bg-zinc-900/90 hover:border-zinc-700'}`}>
                    
                    <div className="flex items-center p-4 gap-4">
                      <CollapsibleTrigger asChild>
                        <button className="p-2 bg-zinc-950 border border-zinc-800 rounded-lg text-zinc-500 hover:text-white transition-all cursor-pointer">
                          {expandedFiles[file.id] ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
                        </button>
                      </CollapsibleTrigger>
                      
                      <div className="p-2.5 bg-zinc-950 border border-zinc-800 rounded-xl">
                        <BookMarked className={`w-5 h-5 ${expandedFiles[file.id] ? 'text-blue-500' : 'text-zinc-600'}`} />
                      </div>

                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                            <span className="text-[9px] font-bold text-blue-500 bg-blue-500/10 px-2 py-0.5 rounded uppercase">{subjectName}</span>
                        </div>
                        <h3 className="text-sm font-bold text-zinc-200 truncate mt-1">{file.original_name}</h3>
                      </div>

                      <div className="text-right hidden sm:block px-4">
                        <p className="text-[10px] font-bold text-zinc-500 uppercase">Chunks</p>
                        <p className="text-xs font-mono text-zinc-300">{fileChunks.length}</p>
                      </div>
                    </div>

                    <CollapsibleContent>
                      <div className="px-8 pb-6 pt-1 ml-10 border-l border-zinc-800/50 space-y-2">
                        {fileChunks.map((chunk) => (
                          <div 
                            key={chunk.id} 
                            className="flex items-center justify-between gap-4 p-3 bg-zinc-900/60 border border-zinc-800/50 rounded-xl hover:bg-zinc-900/90 hover:border-zinc-500 transition-all group/chunk cursor-pointer"
                          >
                            <div className="flex items-center gap-4 flex-1 min-w-0">
                              <span className="text-[10px] font-bold text-zinc-500">#{chunk.chunk_index}</span>
                              <p className="text-xs text-zinc-400 truncate group-hover/chunk:text-zinc-200">{chunk.content}</p>
                            </div>
                            <div className="flex items-center">
                              <Button 
                                variant="ghost" 
                                className="h-9 w-9 p-0 bg-zinc-800 border border-zinc-700 hover:bg-zinc-700 rounded-lg cursor-pointer transition-colors shadow-sm" 
                                onClick={(e) => { e.stopPropagation(); setSelectedChunk(chunk); setEditContent(chunk.content); setIsEditModalOpen(true); }}
                              >
                                <Edit3 className="w-4 h-4 text-zinc-100" />
                              </Button>
                            </div>
                          </div>
                        ))}
                      </div>
                    </CollapsibleContent>
                  </div>
                </Collapsible>
              );
            })
          )}
        </div>
      </div>

{/* ---- Section: Pipeline Overlay ---- */}
<Dialog open={isPipelineModalOpen} onOpenChange={setIsPipelineModalOpen}>
  <DialogContent className="bg-zinc-950 border-zinc-800 text-zinc-200 min-w-[800px] p-10 rounded-2xl border shadow-2xl">
    <DialogHeader className="mb-6">
      <DialogTitle className="text-2xl font-bold flex items-center gap-3 text-white">
        <CloudUpload className="w-6 h-6 text-blue-500" />
        New Pipeline
      </DialogTitle>
    </DialogHeader>

    <div className="space-y-10">
      {/* 1. Knowledge Domain Section */}
      <div className="space-y-2 pb-3">
        <label className="text-[11px] font-mono text-zinc-500 uppercase block tracking-widest">
          1. Subject
        </label>

        <Select onValueChange={setSelectedSubjectId} value={selectedSubjectId}>
          <SelectTrigger className="w-full grid grid-cols-[1fr_20px] items-center bg-zinc-900 border-zinc-800 text-white h-14 rounded-xl cursor-pointer focus:ring-2 focus:ring-blue-500/40 transition-all px-4 text-base shadow-inner [&>svg]:hidden">
            <span className="truncate text-left block">
              <SelectValue placeholder="Select context subject..." />
            </span>
          </SelectTrigger>

          <SelectContent
            position="popper"
            sideOffset={4}
            className="bg-zinc-900 border-zinc-800 rounded-xl max-h-[250px] w-[var(--radix-select-trigger-width)] shadow-2xl"
          >
            {subjects.map((sub) => (
              <SelectItem
                key={sub.id}
                value={sub.id}
                className="text-white focus:bg-blue-600 focus:text-white cursor-pointer py-4 text-base border-b border-zinc-800/50 last:border-0"
              >
                {sub.title}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* 2. Target Asset Section */}
      <div className="space-y-2 pb-3">
        <label className="text-[11px] font-mono text-zinc-500 uppercase block tracking-widest">
          2. Target File
        </label>

        <Select onValueChange={setSelectedFileId} value={selectedFileId}>
          <SelectTrigger className="w-full grid grid-cols-[1fr_20px] items-center bg-zinc-900 border-zinc-800 text-white h-14 rounded-xl cursor-pointer focus:ring-2 focus:ring-blue-500/40 transition-all px-4 text-base shadow-inner overflow-hidden [&>svg]:hidden">
            <span className="truncate text-left block">
              <SelectValue placeholder="Select source book..." />
            </span>
          </SelectTrigger>

          <SelectContent
            position="popper"
            sideOffset={4}
            className="bg-zinc-900 border-zinc-800 rounded-xl max-h-[250px] w-[var(--radix-select-trigger-width)] shadow-2xl"
          >
            {files.map((file) => (
              <SelectItem
                key={file.id}
                value={file.id}
                className="text-white focus:bg-blue-600 focus:text-white cursor-pointer py-4 text-base border-b border-zinc-800/50 last:border-0"
              >
                {file.original_name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* System Information Feedback */}
      <div className="p-5 bg-blue-500/5 border border-blue-500/10 rounded-2xl flex gap-4">
        <Database className="w-5 h-5 text-blue-500 shrink-0 mt-0.5" />
        <p className="text-[13px] text-zinc-400 leading-relaxed">
          Starting the pipeline will initiate semantic segmentation and vector indexing for the selected asset.
        </p>
      </div>

      {/* Operational Controls */}
      <div className="flex flex-col sm:flex-row gap-4 pt-6">
        <Button
          variant="ghost"
          onClick={() => setIsPipelineModalOpen(false)}
          className="flex-1 text-zinc-400 hover:text-red-400 data-[state=open]:bg-transparent hover:bg-red-500/10 h-16 text-sm font-black uppercase tracking-tighter rounded-xl cursor-pointer transition-all border border-transparent hover:border-red-500/20"
        >
          CANCEL
        </Button>

        <Button
          onClick={executePipeline}
          disabled={isProcessing || !selectedSubjectId || !selectedFileId}
          className="flex-[2.5] bg-blue-600 hover:bg-blue-500 text-white h-16 text-base font-black uppercase tracking-tight cursor-pointer transition-all rounded-xl shadow-[0_0_20px_rgba(37,99,235,0.3)] hover:shadow-[0_0_30px_rgba(37,99,235,0.5)] active:scale-[0.98] disabled:cursor-not-allowed disabled:bg-zinc-800 disabled:shadow-none"
        >
          {isProcessing ? (
            <>
              <Loader2 className="w-6 h-6 animate-spin mr-3" />
              PROCESSING...
            </>
          ) : (
            "EXECUTE PIPELINE"
          )}
        </Button>
      </div>
    </div>
  </DialogContent>
</Dialog>

      {/* ---- Section: Edit Modal ---- */}
      <Dialog open={isEditModalOpen} onOpenChange={setIsEditModalOpen}>
        <DialogContent className="bg-zinc-950 border-zinc-800 text-zinc-100 max-w-2xl p-0 rounded-xl overflow-hidden border shadow-2xl">
          <div className="px-6 py-4 border-b border-zinc-800 bg-zinc-900/60 flex items-center justify-between">
            <h2 className="text-sm font-bold">Edit Node Content</h2>
            <X className="w-4 h-4 cursor-pointer text-zinc-500 hover:text-white" onClick={() => setIsEditModalOpen(false)} />
          </div>
          <div className="p-6 bg-zinc-950">
            <Textarea 
              value={editContent} 
              onChange={(e) => setEditContent(e.target.value)}
              className="min-h-[250px] bg-zinc-900/40 border-zinc-800 rounded-xl resize-none text-sm focus:ring-1 focus:ring-blue-500/30 p-4"
            />
          </div>
          <div className="px-6 py-4 border-t border-zinc-800 flex justify-end gap-3 bg-zinc-900/60">
            <Button variant="ghost" onClick={() => setIsEditModalOpen(false)} className="text-xs font-bold hover:bg-zinc-800 cursor-pointer">Discard</Button>
            <Button onClick={handleUpdateChunk} disabled={isProcessing} className="bg-blue-600 hover:bg-blue-500 h-9 px-6 rounded-lg text-xs font-bold text-white cursor-pointer">
              {isProcessing && <Loader2 className="w-3 h-3 animate-spin mr-2" />} Save Changes
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}