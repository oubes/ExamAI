"use client";

import { useState, useCallback, useRef, useEffect } from "react";
import { 
    Loader2, 
    Search, 
    CloudUpload, 
    FileIcon, 
    MoreVertical, 
    Trash2, 
    Download,
    HardDrive,
    LayoutGrid,
    List,
    AlertCircle
} from "lucide-react";

// ---- Services & Types ----
import { storageService, StorageFile } from "@/services/storage.service";

// ---- UI Components ----
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { 
    DropdownMenu, 
    DropdownMenuContent, 
    DropdownMenuItem, 
    DropdownMenuTrigger 
} from "@/components/ui/dropdown-menu";

// ---- Helpers ----
const formatBytes = (bytes: number, decimals = 2) => {
    if (!bytes) return "0 Bytes";
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ["Bytes", "KB", "MB", "GB", "TB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + " " + sizes[i];
};

export default function StoragePage() {
    // ---- State ----
    const [files, setFiles] = useState<StorageFile[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [searchQuery, setSearchQuery] = useState("");
    const [isUploading, setIsUploading] = useState(false);
    const [viewMode, setViewMode] = useState<"grid" | "list">("grid");
    
    const fileInputRef = useRef<HTMLInputElement>(null);

    // ---- Lifecycle ----
    useEffect(() => {
        const fetchFiles = async () => {
            try {
                setIsLoading(true);
                const data = await storageService.listFiles();
                setFiles(Array.isArray(data) ? data : []);
            } catch (error) {
                console.error("Fetch error:", error);
            } finally {
                setIsLoading(false);
            }
        };
        fetchFiles();
    }, []);

    // ---- Handlers ----
    const handleUploadClick = () => {
        fileInputRef.current?.click();
    };

    const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const selectedFile = e.target.files?.[0];
        if (!selectedFile) return;

        setIsUploading(true);
        try {
            const uploadedFile = await storageService.uploadFile(selectedFile, "general");
            setFiles(prev => [uploadedFile, ...prev]);
        } catch (error) {
            console.error("Upload failed:", error);
        } finally {
            setIsUploading(false);
            if (fileInputRef.current) fileInputRef.current.value = "";
        }
    };

    const deleteFile = async (id: string) => {
        try {
            await storageService.deleteFile(id);
            setFiles(prev => prev.filter(f => f.id !== id));
        } catch (error) {
            console.error("Delete failed:", error);
        }
    };

    const filteredFiles = files.filter(f => 
        f.original_name?.toLowerCase().includes(searchQuery.toLowerCase())
    );

    return (
        <div className="flex flex-col min-h-screen bg-[#09090b] text-zinc-100 p-6 lg:p-10">
            
            <header className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 mb-10">
                <div>
                    <div className="flex items-center gap-2 mb-1">
                        <HardDrive className="w-4 h-4 text-blue-500" />
                        <span className="text-xs font-mono uppercase tracking-tighter text-zinc-500">Asset Management</span>
                    </div>
                    <h1 className="text-3xl font-bold tracking-tight">Storage</h1>
                </div>

                <div className="flex items-center gap-3 w-full md:w-auto">
                    <div className="relative flex-1 md:w-64">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
                        <Input 
                            placeholder="Find files..." 
                            className="bg-zinc-900 border-zinc-800 pl-10 focus:ring-blue-500/20 text-zinc-200"
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                        />
                    </div>

                    <input 
                        type="file" 
                        ref={fileInputRef} 
                        onChange={handleFileChange} 
                        className="hidden" 
                    />
                    <Button 
                        onClick={handleUploadClick}
                        disabled={isUploading}
                        className="bg-blue-600 hover:bg-blue-700 text-white gap-2 px-6 shadow-lg shadow-blue-900/20 cursor-pointer"
                    >
                        {isUploading ? <Loader2 className="w-4 h-4 animate-spin" /> : <CloudUpload className="w-4 h-4" />}
                        <span className="hidden sm:inline">Upload File</span>
                    </Button>
                </div>
            </header>

            <div className="flex items-center justify-between mb-6 border-b border-zinc-800/50 pb-4">
                <div className="flex gap-4">
                    <button 
                        onClick={() => setViewMode("grid")}
                        className={`p-2 rounded-md transition-colors cursor-pointer ${viewMode === "grid" ? "bg-zinc-800 text-white" : "text-zinc-500"}`}
                    >
                        <LayoutGrid className="w-4 h-4" />
                    </button>
                    <button 
                        onClick={() => setViewMode("list")}
                        className={`p-2 rounded-md transition-colors cursor-pointer ${viewMode === "list" ? "bg-zinc-800 text-white" : "text-zinc-500"}`}
                    >
                        <List className="w-4 h-4" />
                    </button>
                </div>
                <span className="text-xs text-zinc-500 font-mono">
                    {isLoading ? "Synchronizing..." : `${filteredFiles.length} assets found`}
                </span>
            </div>

            <main className="flex-1">
                {isLoading ? (
                    <div className="flex flex-col items-center justify-center h-64 gap-3">
                        <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />
                        <p className="text-zinc-500 text-sm font-mono uppercase tracking-widest">Loading Repository</p>
                    </div>
                ) : filteredFiles.length === 0 ? (
                    <div className="flex flex-col items-center justify-center h-64 border-2 border-dashed border-zinc-800 rounded-2xl">
                        <FileIcon className="w-10 h-10 text-zinc-700 mb-4" />
                        <p className="text-zinc-500 text-sm italic">No digital assets located.</p>
                    </div>
                ) : (
                    <div className={viewMode === "grid" 
                        ? "grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-5 gap-4" 
                        : "flex flex-col gap-2"
                    }>
                        {filteredFiles.map((file) => (
                            <FileCard 
                                key={file.id} 
                                file={file} 
                                mode={viewMode} 
                                onDelete={() => deleteFile(file.id)} 
                            />
                        ))}
                    </div>
                )}
            </main>
        </div>
    );
}

function FileCard({ file, mode, onDelete }: { file: StorageFile, mode: "grid" | "list", onDelete: () => void }) {
    const fileSize = formatBytes(file.size);
    const uploadDate = new Date(file.created_at).toLocaleDateString();

    if (mode === "list") {
        return (
            <div className="flex items-center justify-between p-3 bg-zinc-900/30 border border-zinc-800/50 rounded-xl hover:bg-zinc-900 transition-colors group">
                <div className="flex items-center gap-4">
                    <div className="relative">
                        <FileIcon className="w-5 h-5 text-blue-400" />
                        {!file.is_processed && <div className="absolute -top-1 -right-1 w-2 h-2 bg-amber-500 rounded-full animate-pulse" />}
                    </div>
                    <span className="text-sm font-medium truncate max-w-[200px] md:max-w-md text-zinc-300">{file.original_name}</span>
                </div>
                <div className="flex items-center gap-6">
                    <span className="text-xs text-zinc-500 font-mono hidden md:block">{fileSize}</span>
                    <span className="text-xs text-zinc-500 hidden md:block">{uploadDate}</span>
                    <FileActions onDelete={onDelete} fileUrl={file.path} status={file.processing_status} />
                </div>
            </div>
        );
    }

    return (
        <div className="flex flex-col bg-zinc-900/40 border border-zinc-800/50 rounded-2xl p-4 hover:border-zinc-700 transition-all group relative">
            <div className="flex justify-between items-start mb-6">
                <div className="p-3 bg-zinc-800/50 rounded-lg group-hover:bg-blue-500/10 transition-colors">
                    <FileIcon className={`w-6 h-6 ${file.is_processed ? 'text-zinc-400 group-hover:text-blue-500' : 'text-amber-500'}`} />
                </div>
                <FileActions onDelete={onDelete} fileUrl={file.path} status={file.processing_status} />
            </div>
            
            <div className="mt-auto">
                <h3 className="text-sm font-semibold text-zinc-200 truncate pr-2" title={file.original_name}>
                    {file.original_name}
                </h3>
                <div className="flex justify-between items-center mt-1">
                    <p className="text-[10px] text-zinc-500 font-mono uppercase">{fileSize}</p>
                    {!file.is_processed && (
                        <span className="text-[9px] text-amber-500 font-mono animate-pulse uppercase">Processing</span>
                    )}
                </div>
            </div>
        </div>
    );
}

function FileActions({ onDelete, fileUrl, status }: { onDelete: () => void, fileUrl: string, status: string }) {
    const handleDownload = () => {
        window.open(fileUrl, "_blank");
    };

    return (
        <DropdownMenu>
            <DropdownMenuTrigger asChild>
                <button className="p-1 hover:bg-zinc-800 rounded-md transition-colors text-zinc-500 cursor-pointer">
                    <MoreVertical className="w-4 h-4" />
                </button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="bg-zinc-950 border-zinc-800 text-zinc-300">
                <DropdownMenuItem 
                    onClick={handleDownload}
                    className="gap-2 cursor-pointer focus:bg-zinc-900 focus:text-white"
                >
                    <Download className="w-4 h-4" /> Download
                </DropdownMenuItem>
                <DropdownMenuItem 
                    onClick={onDelete}
                    className="gap-2 cursor-pointer text-red-500 focus:bg-red-500/10 focus:text-red-500"
                >
                    <Trash2 className="w-4 h-4" /> Delete
                </DropdownMenuItem>
                {status === "failed" && (
                    <DropdownMenuItem className="gap-2 text-amber-500 text-xs cursor-default">
                        <AlertCircle className="w-3 h-3" /> Processing Failed
                    </DropdownMenuItem>
                )}
            </DropdownMenuContent>
        </DropdownMenu>
    );
}