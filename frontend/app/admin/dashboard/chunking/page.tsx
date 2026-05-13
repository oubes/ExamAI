"use client";

import React, { useState, useEffect, useMemo } from "react";
import { 
  Loader2, Search, FileIcon, ChevronDown, ChevronRight, 
  Play, Edit3, Trash2, Database, Layers, BookMarked, Cpu, X, AlertCircle
} from "lucide-react";
import { toast } from "sonner";

// ---- UI Components ----
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Dialog, DialogContent, DialogFooter } from "@/components/ui/dialog";
import { Textarea } from "@/components/ui/textarea";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

// ---- Services ----
import { storageService, StorageFile } from "@/services/storage.service";
import { questionService, ChunkResponse } from "@/services/chunk.service";
import { educationService, SubjectResponse } from "@/services/subjects.service";

// ---- Section: Utilities ----
const formatBytes = (bytes: number) => {
  if (!bytes) return "0 Bytes";
  const k = 1024;
  const sizes = ["Bytes", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
};

export default function UnifiedStoragePage() {
  // ---- Section: State Management ----
  const [files, setFiles] = useState<StorageFile[]>([]);
  const [subjects, setSubjects] = useState<SubjectResponse[]>([]);
  const [chunksMap, setChunksMap] = useState<Record<string, ChunkResponse[]>>({});
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [expandedFiles, setExpandedFiles] = useState<Record<string, boolean>>({});
  
  const [isPipelineModalOpen, setIsPipelineModalOpen] = useState(false);
  const [targetFile, setTargetFile] = useState<StorageFile | null>(null);
  const [selectedSubjectId, setSelectedSubjectId] = useState<string>("");
  const [isProcessing, setIsProcessing] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [selectedChunk, setSelectedChunk] = useState<ChunkResponse | null>(null);
  const [editContent, setEditContent] = useState("");
  const [isDeleteConfirmOpen, setIsDeleteConfirmOpen] = useState(false);
  const [chunkToDelete, setChunkToDelete] = useState<ChunkResponse | null>(null);

  // ---- Section: Data Fetching ----
  const fetchInitialData = async () => {
    try {
      setIsLoading(true);
      const [filesData, subjectsData] = await Promise.all([
        storageService.listFiles(),
        educationService.listSubjects()
      ]);
      setFiles(Array.isArray(filesData) ? filesData : []);
      setSubjects(subjectsData.items || []);
    } catch (error) {
      toast.error("Environment sync failed");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => { fetchInitialData(); }, []);

  const toggleFileExpansion = async (fileId: string) => {
    const isExpanding = !expandedFiles[fileId];
    setExpandedFiles(prev => ({ ...prev, [fileId]: isExpanding }));

    if (isExpanding && !chunksMap[fileId]) {
      try {
        const response = await questionService.listChunks(); 
        const fileChunks = response.items.filter(c => c.book_id === fileId);
        setChunksMap(prev => ({ ...prev, [fileId]: fileChunks }));
      } catch (error) {
        toast.error("Segment retrieval failed");
      }
    }
  };

  // ---- Section: Actions ----
  const executePipeline = async () => {
    if (!targetFile || !selectedSubjectId) return;
    try {
      setIsProcessing(true);
      await questionService.runSegmentationPipeline(selectedSubjectId, targetFile.id);
      toast.success("Pipeline executed");
      setIsPipelineModalOpen(false);
      const response = await questionService.listChunks();
      setChunksMap(prev => ({ 
        ...prev, 
        [targetFile.id]: response.items.filter(c => c.book_id === targetFile.id) 
      }));
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
      setChunksMap(prev => ({
        ...prev,
        [selectedChunk.book_id]: prev[selectedChunk.book_id].map(c => 
          c.id === selectedChunk.id ? { ...c, content: editContent } : c
        )
      }));
    } catch (error) {
      toast.error("Update failed");
    } finally {
      setIsProcessing(false);
    }
  };

  const confirmDelete = async () => {
    if (!chunkToDelete) return;
    try {
      setIsProcessing(true);
      await questionService.deleteChunk(chunkToDelete.id);
      toast.success("Purged");
      setChunksMap(prev => ({
        ...prev,
        [chunkToDelete.book_id]: prev[chunkToDelete.book_id].filter(c => c.id !== chunkToDelete.id)
      }));
      setIsDeleteConfirmOpen(false);
    } catch (error) {
      toast.error("Purge failed");
    } finally {
      setIsProcessing(false);
    }
  };

  const filteredFiles = useMemo(() => {
    return files.filter(f => f.original_name?.toLowerCase().includes(searchQuery.toLowerCase()));
  }, [files, searchQuery]);

  const stats = useMemo(() => ({
    totalFiles: files.length,
    totalSubjects: subjects.length,
    totalChunks: Object.values(chunksMap).flat().length
  }), [files, subjects, chunksMap]);

  return (
    <div className="min-h-screen bg-[#020203] text-zinc-100 p-6 lg:p-12 selection:bg-blue-500/30">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <header className="flex flex-col md:flex-row justify-between items-start md:items-end gap-6 mb-12">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <Cpu className="w-4 h-4 text-blue-500" />
              <span className="text-[10px] font-bold uppercase tracking-[0.2em] text-zinc-500">Knowledge Lab</span>
            </div>
            <h1 className="text-4xl font-extrabold tracking-tight text-white lg:text-5xl">
              Processing<span className="text-blue-600">.</span>
            </h1>
          </div>

          <div className="relative w-full md:w-72">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
            <Input 
              placeholder="Search assets..." 
              className="bg-zinc-900/60 border-zinc-800 h-11 pl-10 rounded-xl focus:ring-1 focus:ring-blue-500/50"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
        </header>

        {/* Stats */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-12">
          {[
            { label: "Assets", value: stats.totalFiles, icon: Database, color: "text-blue-500" },
            { label: "Subjects", value: stats.totalSubjects, icon: BookMarked, color: "text-emerald-500" },
            { label: "Segments", value: stats.totalChunks, icon: Layers, color: "text-amber-500" },
          ].map((s, i) => (
            <div key={i} className="bg-zinc-900/60 border border-zinc-800/50 p-5 rounded-2xl flex items-center gap-4 hover:bg-zinc-900/90 transition-colors">
              <div className={`p-2.5 bg-zinc-950 border border-zinc-800 rounded-xl ${s.color}`}>
                <s.icon className="w-5 h-5" />
              </div>
              <div>
                <p className="text-[10px] font-bold uppercase text-zinc-600 tracking-wider">{s.label}</p>
                <p className="text-xl font-bold text-white">{s.value}</p>
              </div>
            </div>
          ))}
        </div>

        {/* Main List */}
        <div className="space-y-3">
          {isLoading ? (
            <div className="flex flex-col items-center justify-center py-20 gap-3">
              <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />
              <p className="text-zinc-600 text-[10px] font-mono uppercase tracking-widest">Syncing...</p>
            </div>
          ) : (
            filteredFiles.map((file) => (
              <Collapsible key={file.id} open={expandedFiles[file.id]} onOpenChange={() => toggleFileExpansion(file.id)}>
                <div className={`rounded-2xl border transition-all ${expandedFiles[file.id] ? 'bg-zinc-900/90 border-zinc-700 shadow-xl' : 'bg-zinc-900/60 border-zinc-800/50 hover:bg-zinc-900/90 hover:border-zinc-700'}`}>
                  
                  <div className="flex items-center p-4 gap-4">
                    <CollapsibleTrigger asChild>
                      <button className="p-2 bg-zinc-950 border border-zinc-800 rounded-lg text-zinc-500 hover:text-white transition-all cursor-pointer active:scale-95">
                        {expandedFiles[file.id] ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
                      </button>
                    </CollapsibleTrigger>
                    
                    <div className="p-2.5 bg-zinc-950 border border-zinc-800 rounded-xl">
                      <FileIcon className={`w-5 h-5 ${expandedFiles[file.id] ? 'text-blue-500' : 'text-zinc-600'}`} />
                    </div>

                    <div className="flex-1 min-w-0">
                      <h3 className="text-sm font-bold text-zinc-200 truncate">{file.original_name}</h3>
                      <p className="text-[10px] font-mono text-zinc-600 uppercase mt-0.5">{formatBytes(file.size)}</p>
                    </div>

                    <Button 
                      onClick={() => { setTargetFile(file); setIsPipelineModalOpen(true); }}
                      className="bg-blue-600 hover:bg-blue-500 text-white h-9 px-6 rounded-lg font-bold text-[10px] tracking-wider transition-all cursor-pointer shadow-lg shadow-blue-900/20"
                    >
                      <Play className="w-3 h-3 mr-2 fill-current" /> RUN
                    </Button>
                  </div>

                  <CollapsibleContent>
                    <div className="px-8 pb-6 pt-1 ml-10 border-l border-zinc-800/50 space-y-2">
                      {!chunksMap[file.id] ? (
                        <div className="flex items-center gap-2 text-zinc-600 py-4 text-[10px] font-mono uppercase">
                          <Loader2 className="w-3 h-3 animate-spin text-blue-500" /> streaming...
                        </div>
                      ) : (
                        chunksMap[file.id].map((chunk) => (
                          <div key={chunk.id} className="flex items-center justify-between gap-4 p-3 bg-zinc-950/30 border border-zinc-900/50 rounded-xl hover:bg-zinc-900/60 hover:border-zinc-700 transition-all group/chunk">
                            <div className="flex items-center gap-4 flex-1 min-w-0">
                              <span className="text-[10px] font-bold text-blue-500 bg-blue-500/5 px-2 py-1 rounded border border-blue-500/10">#{chunk.chunk_index}</span>
                              <p className="text-xs text-zinc-400 truncate italic group-hover/chunk:text-zinc-200">"{chunk.content}"</p>
                            </div>
                            <div className="flex items-center gap-1.5">
                              <Button variant="ghost" className="h-8 w-8 p-0 hover:bg-zinc-800 rounded-lg cursor-pointer" onClick={() => { setSelectedChunk(chunk); setEditContent(chunk.content); setIsEditModalOpen(true); }}>
                                <Edit3 className="w-3.5 h-3.5 text-zinc-500" />
                              </Button>
                              <Button variant="ghost" className="h-8 w-8 p-0 hover:bg-red-950/30 rounded-lg cursor-pointer" onClick={() => { setChunkToDelete(chunk); setIsDeleteConfirmOpen(true); }}>
                                <Trash2 className="w-3.5 h-3.5 text-zinc-600" />
                              </Button>
                            </div>
                          </div>
                        ))
                      )}
                    </div>
                  </CollapsibleContent>
                </div>
              </Collapsible>
            ))
          )}
        </div>
      </div>

      {/* Edit Modal */}
      <Dialog open={isEditModalOpen} onOpenChange={setIsEditModalOpen}>
        <DialogContent className="bg-[#0c0c0e] border-zinc-800 text-zinc-100 max-w-2xl p-0 rounded-xl overflow-hidden border shadow-2xl">
          <div className="px-6 py-4 border-b border-zinc-800 flex items-center justify-between bg-zinc-900/60">
            <h2 className="text-sm font-bold">Edit Segment</h2>
            <X className="w-4 h-4 cursor-pointer text-zinc-500 hover:text-white" onClick={() => setIsEditModalOpen(false)} />
          </div>
          <div className="p-6 bg-zinc-950/20">
            <Textarea 
              value={editContent} 
              onChange={(e) => setEditContent(e.target.value)}
              className="min-h-[300px] bg-zinc-950 border-zinc-800 rounded-lg resize-none text-sm focus-visible:ring-1 focus-visible:ring-blue-500/30"
            />
          </div>
          <div className="px-6 py-4 border-t border-zinc-800 flex justify-end gap-3 bg-zinc-900/60">
            <Button variant="ghost" onClick={() => setIsEditModalOpen(false)} className="text-xs font-bold cursor-pointer hover:bg-zinc-800">Discard</Button>
            <Button onClick={handleUpdateChunk} disabled={isProcessing} className="bg-blue-600 hover:bg-blue-500 h-9 px-6 rounded-lg text-xs font-bold cursor-pointer transition-all">
              {isProcessing && <Loader2 className="w-3 h-3 animate-spin mr-2" />} Save Changes
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* Delete Modal */}
      <Dialog open={isDeleteConfirmOpen} onOpenChange={setIsDeleteConfirmOpen}>
        <DialogContent className="bg-[#0c0c0e] border-zinc-800 max-w-sm p-6 rounded-xl text-center border shadow-2xl">
          <AlertCircle className="w-10 h-10 text-red-500 mx-auto mb-4" />
          <h3 className="font-bold text-white mb-2">Delete Node #{chunkToDelete?.chunk_index}?</h3>
          <p className="text-xs text-zinc-500 mb-6">This action cannot be undone.</p>
          <div className="flex gap-3">
            <Button variant="ghost" className="flex-1 rounded-lg cursor-pointer hover:bg-zinc-800" onClick={() => setIsDeleteConfirmOpen(false)}>Cancel</Button>
            <Button className="flex-1 bg-red-600 hover:bg-red-500 rounded-lg text-white cursor-pointer shadow-lg shadow-red-900/20" onClick={confirmDelete} disabled={isProcessing}>
              {isProcessing ? <Loader2 className="w-3 h-3 animate-spin" /> : "Delete"}
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* Pipeline Modal */}
      <Dialog open={isPipelineModalOpen} onOpenChange={setIsPipelineModalOpen}>
        <DialogContent className="bg-[#0c0c0e] border-zinc-800 max-w-xs p-6 rounded-xl border shadow-2xl">
          <h2 className="text-sm font-bold mb-4">Launch Pipeline</h2>
          <Select onValueChange={setSelectedSubjectId} value={selectedSubjectId}>
            <SelectTrigger className="bg-zinc-950 border-zinc-800 rounded-lg h-10 text-xs cursor-pointer">
              <SelectValue placeholder="Select Subject" />
            </SelectTrigger>
            <SelectContent className="bg-zinc-950 border-zinc-800">
              {subjects.map((sub) => (
                <SelectItem key={sub.id} value={sub.id} className="text-xs cursor-pointer">{sub.title}</SelectItem>
              ))}
            </SelectContent>
          </Select>
          <div className="flex gap-2 mt-6">
            <Button variant="ghost" className="flex-1 rounded-lg text-xs cursor-pointer hover:bg-zinc-800" onClick={() => setIsPipelineModalOpen(false)}>Abort</Button>
            <Button onClick={executePipeline} disabled={isProcessing || !selectedSubjectId} className="flex-1 bg-blue-600 hover:bg-blue-500 rounded-lg text-xs font-bold cursor-pointer transition-all shadow-lg shadow-blue-900/20">
              {isProcessing ? <Loader2 className="w-3 h-3 animate-spin" /> : "Start"}
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}