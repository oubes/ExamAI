"use client";

import React, { useState, useEffect, useMemo } from "react";
import { 
  Loader2, Search, ChevronDown, ChevronRight, 
  Edit3, BookMarked, Cpu, X, AlertCircle, Plus, CloudUpload, Database, Maximize2,
  Trash2, HelpCircle, Play, Undo2
} from "lucide-react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Textarea } from "@/components/ui/textarea";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

import { storageService, StorageFile } from "@/services/storage.service";
import { questionService, ChunkResponse } from "@/services/chunk.service";
import { educationService, SubjectResponse } from "@/services/subjects.service";

export default function UnifiedStoragePage() {
  const [files, setFiles] = useState<StorageFile[]>([]);
  const [subjects, setSubjects] = useState<SubjectResponse[]>([]);
  const [allChunks, setAllChunks] = useState<ChunkResponse[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [expandedFiles, setExpandedFiles] = useState<Record<string, boolean>>({});
  
  const [isPipelineModalOpen, setIsPipelineModalOpen] = useState(false);
  const [selectedFileId, setSelectedFileId] = useState<string>("");
  const [selectedSubjectId, setSelectedSubjectId] = useState<string>("");
  const [isProcessing, setIsProcessing] = useState(false);

  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [selectedChunk, setSelectedChunk] = useState<ChunkResponse | null>(null);
  const [editContent, setEditContent] = useState("");

  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [fileToDelete, setFileToDelete] = useState<string | null>(null);

  // ---- Fetch Initial Data ----
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

  const processedFiles = useMemo(() => {
    const fileIdsWithChunks = new Set(allChunks.map(c => c.book_id));
    return files.filter(f => fileIdsWithChunks.has(f.id))
                .filter(f => f.original_name?.toLowerCase().includes(searchQuery.toLowerCase()));
  }, [files, allChunks, searchQuery]);

  const getChunksForFile = (fileId: string) => {
    return allChunks
      .filter(c => c.book_id === fileId)
      .sort((a, b) => a.chunk_index - b.chunk_index);
  };
  
  const getSubjectName = (subjectId: string) => {
    return subjects.find(s => s.id === subjectId)?.title || "Unknown Subject";
  };

  // ---- Pipeline Execution ----
  const handleRunPipeline = async (subjectId: string, fileId: string) => {
    try {
      setIsProcessing(true);
      await questionService.runSegmentationPipeline(subjectId, fileId);
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

  const executePipeline = async () => {
    if (!selectedFileId || !selectedSubjectId) return;
    await handleRunPipeline(selectedSubjectId, selectedFileId);
  };

  // ---- Update Chunk ----
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

  // ---- Delete Last Chunk ----
  const handleDeleteLastChunk = async (e: React.MouseEvent, fileId: string) => {
    e.stopPropagation();
    const fileChunks = getChunksForFile(fileId);
    if (fileChunks.length === 0) return;

    const lastChunk = fileChunks[fileChunks.length - 1];

    try {
      setIsProcessing(true);
      await questionService.deleteChunk(lastChunk.id);
      toast.success(`Chunk #${lastChunk.chunk_index} removed`);
      setAllChunks(prev => prev.filter(c => c.id !== lastChunk.id));
    } catch (error) {
      toast.error("Failed to remove last chunk");
    } finally {
      setIsProcessing(false);
    }
  };

  // ---- Delete Full Group ----
  const handleDeleteFileGroup = async () => {
    if (!fileToDelete) return;
    const relevantChunks = getChunksForFile(fileToDelete);
    if (relevantChunks.length === 0) return;
    const subjectId = relevantChunks[0].subject_id;

    try {
        setIsProcessing(true);
        await questionService.deleteAllChunksBySubjectAndBook(subjectId, fileToDelete);
        toast.warning("All segments for this asset have been removed.");
        setAllChunks(prev => prev.filter(c => c.book_id !== fileToDelete));
        setIsDeleteDialogOpen(false);
        setFileToDelete(null);
    } catch (error) {
        toast.error("Deletion failed");
    } finally {
        setIsProcessing(false);
    }
  };

  const openDeleteDialog = (e: React.MouseEvent, fileId: string) => {
    e.stopPropagation();
    setFileToDelete(fileId);
    setIsDeleteDialogOpen(true);
  };

  return (
    <div className="min-h-screen bg-[#020203] text-zinc-100 p-6 lg:p-12 selection:bg-blue-500/30">
      <div className="max-w-6xl mx-auto">
        <header className="flex flex-col md:flex-row justify-between items-start md:items-end gap-6 mb-12">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <Cpu className="w-4 h-4 text-blue-500" />
              <span className="text-[10px] font-bold uppercase tracking-[0.2em] text-zinc-500">Chunking</span>
            </div>
            <h1 className="text-3xl font-bold tracking-tight">Segments</h1>
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

        <div className="space-y-4">
          {isLoading ? (
            <div className="flex flex-col items-center justify-center py-20 gap-3">
              <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />
              <p className="text-zinc-600 text-[10px] font-mono uppercase tracking-widest">Loading Chunks...</p>
            </div>
          ) : processedFiles.length === 0 ? (
            <div className="text-center py-20 border-2 border-dashed border-zinc-900 rounded-3xl">
                <p className="text-zinc-500 text-xl font-bold">No processed chunks found.</p>
            </div>
          ) : (
            processedFiles.map((file) => {
              const fileChunks = getChunksForFile(file.id);
              const subjectId = fileChunks[0]?.subject_id || "";
              const subjectName = getSubjectName(subjectId);
              const totalChunksInDB = fileChunks[0]?.total_chunks || fileChunks.length;

              return (
                <Collapsible key={file.id} open={expandedFiles[file.id]} onOpenChange={() => setExpandedFiles(prev => ({ ...prev, [file.id]: !prev[file.id] }))}>
                  <div className={`group rounded-2xl border transition-all duration-200 ${expandedFiles[file.id] ? 'bg-zinc-900/90 border-zinc-700 shadow-xl' : 'bg-zinc-900/60 border-zinc-800/50 hover:bg-zinc-900/90 hover:border-zinc-700'}`}>
                    
                    <div className="flex items-center p-4 gap-4">
                      <CollapsibleTrigger asChild>
                        <button className="p-2 bg-zinc-950 border border-zinc-800 rounded-lg text-zinc-500 hover:text-white transition-all cursor-pointer">
                          {expandedFiles[file.id] ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
                        </button>
                      </CollapsibleTrigger>
                      
                      <div className="p-2.5 bg-zinc-950 border border-zinc-800 rounded-xl transition-all duration-300">
                        <BookMarked className={`w-5 h-5 transition-transform duration-300 group-hover:scale-110 ${expandedFiles[file.id] ? 'text-blue-500' : 'text-zinc-600'}`} />
                      </div>

                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <span className="text-[9px] font-bold text-blue-500 bg-blue-500/10 px-2 py-0.5 rounded uppercase">{subjectName}</span>
                        </div>
                        <h3 className="text-sm font-bold text-zinc-200 truncate mt-1">{file.original_name}</h3>
                      </div>

                      <div className="text-right hidden sm:flex items-center gap-3 px-4">
                        <div className="flex flex-col mr-2">
                          <p className="text-[10px] font-bold text-zinc-500 uppercase">Segments</p>
                          <p className="text-xs font-mono text-zinc-300">
                            {fileChunks.length}
                          </p>
                        </div>
                          
                          <Button 
                            variant="ghost" 
                            disabled={isProcessing || fileChunks.length === 0}
                            onClick={(e) => handleDeleteLastChunk(e, file.id)}
                            className="h-10 px-3 gap-2 bg-amber-500/10 text-amber-500 hover:bg-amber-500 hover:text-black border border-amber-500/20 cursor-pointer transition-all rounded-xl text-[10px] font-bold uppercase"
                          >
                            <Undo2 className="w-3 h-3" />
                            Pop Last
                          </Button>

                          <Button 
                            variant="ghost" 
                            disabled={isProcessing}
                            onClick={(e) => {
                              e.stopPropagation();
                              handleRunPipeline(subjectId, file.id);
                            }}
                            className="h-10 px-3 gap-2 bg-emerald-500/10 text-emerald-500 hover:bg-emerald-500 hover:text-white border border-emerald-500/20 cursor-pointer transition-all rounded-xl text-[10px] font-bold uppercase"
                          >
                            {isProcessing ? <Loader2 className="w-3 h-3 animate-spin" /> : <Play className="w-3 h-3 fill-current" />}
                            Run Pipeline
                          </Button>

                          <Button 
                            variant="ghost" 
                            onClick={(e) => openDeleteDialog(e, file.id)}
                            className="h-10 w-10 p-0 text-red-600 hover:text-red-500 hover:bg-red-500/10 cursor-pointer transition-all flex items-center justify-center border-none shadow-none"
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                      </div>
                    </div>

                    <CollapsibleContent>
                      <div className="px-8 pb-6 pt-1 ml-10 border-l border-zinc-800/50 space-y-2">
                        {fileChunks.map((chunk) => (
                          <div 
                            key={chunk.id} 
                            className="flex items-center justify-between gap-4 p-3 bg-zinc-900/40 border border-zinc-800/50 rounded-xl hover:bg-zinc-800/80 hover:border-blue-500/50 hover:shadow-lg hover:shadow-blue-500/5 transition-all duration-300 group/chunk cursor-pointer"
                          >
                            <div className="flex items-center gap-4 flex-1 min-w-0">
                              <span className="text-[10px] font-bold text-zinc-500">#{chunk.chunk_index}</span>
                              <p className="text-xs text-zinc-400 truncate group-hover/chunk:text-zinc-100">{chunk.content}</p>
                            </div>
                            <div className="flex items-center">
                              <Button 
                                variant="ghost" 
                                className="h-9 w-9 p-0 bg-zinc-800/50 border border-zinc-700 hover:bg-blue-600 hover:border-blue-500 rounded-lg cursor-pointer transition-all shadow-sm" 
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

      <Dialog open={isPipelineModalOpen} onOpenChange={setIsPipelineModalOpen}>
        <DialogContent className="bg-zinc-950 border-zinc-800 text-zinc-200 w-[92vw] max-w-[1100px] p-10 rounded-2xl border shadow-2xl overflow-hidden focus-visible:outline-none [&>button]:hidden">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setIsPipelineModalOpen(false)}
            className="absolute right-6 top-6 rounded-xl hover:bg-red-500/10 text-zinc-500 hover:text-red-500 cursor-pointer transition-all duration-200 z-50 border border-transparent hover:border-red-500/20"
          >
            <X className="w-5 h-5" />
          </Button>

          <DialogHeader className="mb-6">
            <DialogTitle className="text-2xl font-bold flex items-center gap-3 text-white">
              <CloudUpload className="w-6 h-6 text-blue-500" />
              New Pipeline
            </DialogTitle>
          </DialogHeader>

          <div className="space-y-10 min-w-0">
          <div className="space-y-2 pb-3 min-w-0 text-left">
            <label className="text-[16px] font-mono text-zinc-500 uppercase block tracking-widest text-left">1.Subject</label>
            <Select onValueChange={setSelectedSubjectId} value={selectedSubjectId}>
              <SelectTrigger className="w-full max-w-full flex items-center justify-start bg-zinc-900 border border-zinc-800 text-white h-14 rounded-xl px-4 text-base shadow-inner overflow-hidden min-w-0 cursor-pointer text-left">
                <span className="flex-1 min-w-0 truncate text-left">
                  <SelectValue placeholder="Select context subject..." />
                </span>
              </SelectTrigger>
              <SelectContent position="popper" sideOffset={4} className="bg-zinc-900 border-zinc-800 rounded-xl max-h-[250px] w-[var(--radix-select-trigger-width)] shadow-2xl">
                {subjects.map((sub) => (
                  <SelectItem key={sub.id} value={sub.id} className="text-white cursor-pointer py-4 pl-5 pr-10 text-base border-b border-zinc-800/50 last:border-0 focus:bg-zinc-800 hover:bg-zinc-800 min-w-0">
                    <span className="block truncate min-w-0">{sub.title}</span>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2 pb-3 min-w-0 text-left">
            <label className="text-[16px] font-mono text-zinc-500 uppercase block tracking-widest text-left">2.Target File</label>
            <Select onValueChange={setSelectedFileId} value={selectedFileId}>
              <SelectTrigger className="w-full max-w-full flex items-center justify-start bg-zinc-900 border border-zinc-800 text-white h-14 rounded-xl px-4 text-base shadow-inner overflow-hidden min-w-0 cursor-pointer text-left">
                <span className="flex-1 min-w-0 truncate text-left">
                  <SelectValue placeholder="Select source book..." />
                </span>
              </SelectTrigger>
              <SelectContent position="popper" sideOffset={4} className="bg-zinc-900 border-zinc-800 rounded-xl max-h-[250px] w-[var(--radix-select-trigger-width)] shadow-2xl">
                {files.map((file) => (
                  <SelectItem key={file.id} value={file.id} className="text-white cursor-pointer py-4 pl-5 pr-10 text-base border-b border-zinc-800/50 last:border-0 focus:bg-zinc-800 hover:bg-zinc-800 min-w-0">
                    <span className="block truncate min-w-0">{file.original_name}</span>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

            <div className="p-5 bg-blue-500/5 border border-blue-500/10 rounded-2xl flex gap-4 min-w-0">
              <Database className="w-5 h-5 text-blue-500 shrink-0 mt-0.5" />
              <p className="text-[13px] text-zinc-400 leading-relaxed min-w-0">Starting the pipeline will initiate semantic segmentation.</p>
            </div>

            <div className="flex flex-col sm:flex-row gap-4 pt-6 min-w-0">
              <Button
                variant="ghost"
                onClick={() => setIsPipelineModalOpen(false)}
                className="flex-1 h-12 bg-zinc-900/50 hover:bg-red-600/20 hover:text-red-500 rounded-xl transition-all font-bold border border-zinc-800 cursor-pointer"
              >
                CANCEL
              </Button>
              <Button
                onClick={executePipeline}
                disabled={isProcessing || !selectedSubjectId || !selectedFileId}
                className="flex-2 h-12 bg-blue-600 hover:bg-blue-500 text-white font-bold rounded-xl shadow-lg shadow-blue-600/20 active:scale-[0.98] transition-all cursor-pointer"
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

      <Dialog open={isEditModalOpen} onOpenChange={setIsEditModalOpen}>
        <DialogContent className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[95vw] max-w-5xl h-[80vh] bg-zinc-950 border border-zinc-800 shadow-[0_0_50px_-12px_rgba(0,0,0,0.5)] p-0 flex flex-col rounded-2xl overflow-hidden focus-visible:outline-none">
          <DialogHeader className="p-6 border-b border-zinc-800/50 bg-zinc-900/30 shrink-0 flex flex-row items-center justify-between space-y-0">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-500/10 rounded-lg">
                <Maximize2 className="w-4 h-4 text-blue-500" />
              </div>
              <div>
                <DialogTitle className="text-sm font-bold text-white">Chunk Index: {selectedChunk?.chunk_index}</DialogTitle>
                <p className="text-[10px] text-zinc-500 font-mono uppercase tracking-tighter">Chunk ID: {selectedChunk?.id?.slice(0, 8)}</p>
              </div>
            </div>
            <Button variant="ghost" size="icon" onClick={() => setIsEditModalOpen(false)} className="rounded-full hover:bg-zinc-800 text-zinc-400 cursor-pointer transition-colors">
              <X className="w-4 h-4" />
            </Button>
          </DialogHeader>

          <div className="flex-1 overflow-hidden relative flex flex-col p-6 bg-[#020203]">
              <div className="relative flex-1 flex flex-col border border-zinc-800 bg-zinc-900/20 rounded-xl overflow-hidden focus-within:border-blue-500/50 transition-colors">
                <Textarea 
                  value={editContent} 
                  onChange={(e) => setEditContent(e.target.value)}
                  className="flex-1 w-full bg-transparent border-none resize-none p-6 pr-4 text-sm leading-relaxed text-zinc-300 focus-visible:ring-0 placeholder:text-zinc-700 overflow-y-auto 
                  [&::-webkit-scrollbar]:w-1.5
                  [&::-webkit-scrollbar-track]:bg-transparent
                  [&::-webkit-scrollbar-thumb]:bg-zinc-800
                  [&::-webkit-scrollbar-thumb]:rounded-full
                  hover:[&::-webkit-scrollbar-thumb]:bg-zinc-700
                  transition-all"
                  placeholder="Analyze and edit node content..."
                />
                <div className="absolute bottom-4 right-6 text-[9px] font-mono text-zinc-600 bg-zinc-950/50 px-2 py-1 rounded border border-zinc-800/50 backdrop-blur-sm pointer-events-none">
                  CHAR_COUNT: {editContent.length}
                </div>
              </div>
          </div>

          <div className="p-6 border-t border-zinc-800/50 bg-zinc-900/30 flex items-center justify-between shrink-0">
             <div className="flex gap-3 w-full sm:w-auto flex-1 sm:flex-none">
              <Button 
                variant="ghost" 
                onClick={() => setIsEditModalOpen(false)} 
                className="flex-1 bg-zinc-900 border border-white/5 text-zinc-400 hover:bg-red-900/40 hover:text-red-500 h-10 text-xs font-bold uppercase rounded-lg cursor-pointer transition-all duration-300"
              >
                Discard
              </Button>
              <Button 
                onClick={handleUpdateChunk} 
                disabled={isProcessing} 
                className="flex-[2] bg-blue-600 hover:bg-blue-500 text-white h-10 rounded-lg text-xs font-bold shadow-lg shadow-blue-900/20 cursor-pointer transition-all px-8"
              >
                {isProcessing ? <Loader2 className="w-3 h-3 animate-spin mr-2" /> : "COMMIT CHANGES"}
              </Button>
             </div>
          </div>
        </DialogContent>
      </Dialog>

      <Dialog open={isDeleteDialogOpen} onOpenChange={setIsDeleteDialogOpen}>
        <DialogContent className="bg-zinc-950 border-zinc-800 text-zinc-200 max-w-md p-8 rounded-2xl border shadow-2xl">
          <div className="flex flex-col items-center text-center">
            <div className="w-16 h-16 bg-red-500/10 rounded-full flex items-center justify-center mb-4">
                <HelpCircle className="w-8 h-8 text-red-500" />
            </div>
            <DialogTitle className="text-xl font-bold text-white mb-2">Confirm Deletion</DialogTitle>
            <p className="text-zinc-400 text-sm leading-relaxed mb-8">
                This action will permanently remove all processed segments associated with this asset. This cannot be undone.
            </p>
            <div className="flex w-full gap-3">
              <Button 
                variant="ghost" 
                onClick={() => setIsDeleteDialogOpen(false)}
                className="flex-1 h-12 bg-zinc-900 border border-zinc-800 text-zinc-300 font-bold rounded-xl cursor-pointer"
              >
                CANCEL
              </Button>
              <Button 
                onClick={handleDeleteFileGroup}
                disabled={isProcessing}
                className="flex-1 h-12 bg-red-600 hover:bg-red-500 text-white font-bold rounded-xl shadow-lg shadow-red-900/20 cursor-pointer"
              >
                {isProcessing ? <Loader2 className="w-4 h-4 animate-spin" /> : "DELETE ALL"}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}