"use client";

import { useState, useEffect, useCallback } from "react";
import { 
    Loader2, Mail, Shield, Zap, Target, 
    Edit3, RefreshCw, AlertCircle, 
    BarChart3, Fingerprint, Activity, X, Key,
    Cpu
} from "lucide-react";

// ---- Services & Types ----
import { profileService } from "@/services/profile.service";

// ---- UI Components ----
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { 
    Dialog, DialogContent, DialogHeader, DialogTitle, 
    DialogClose, DialogDescription 
} from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";

export default function ProfilePage() {
    // ---- State ----
    const [profile, setProfile] = useState<any>(null);
    const [stats, setStats] = useState<any>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);

    // ---- Orchestrated Data Fetching ----
    const fetchProfileData = useCallback(async () => {
        try {
            setIsLoading(true);
            setError(null);
            
            const [profileRes, statsRes] = await Promise.all([
                profileService.getMyProfile(),
                profileService.getProfileStats()
            ]);

            setProfile(profileRes);
            setStats(statsRes);
        } catch (err: any) {
            setError(err.message || "Neural link synchronization failed.");
        } finally {
            setIsLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchProfileData();
    }, [fetchProfileData]);

    const handleUpdate = (updatedProfile: any) => {
        setProfile(updatedProfile);
    };

    if (isLoading) {
        return (
            <div className="flex flex-col items-center justify-center min-h-screen bg-[#09090b] gap-3">
                <Loader2 className="w-8 h-8 text-blue-500 animate-spin"/>
                <p className="text-zinc-500 text-sm font-mono uppercase tracking-widest text-center">
                    Reconstructing Identity<br/>
                    <span className="opacity-50 text-[10px]">Accessing Secure Nodes...</span>
                </p>
            </div>
        );
    }

    return (
        <div className="flex flex-col min-h-screen bg-[#09090b] text-zinc-100 p-6 lg:p-12">
            
            <header className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 mb-3">
                <div>
                    <div className="flex items-center gap-2 mb-1">
                        <Fingerprint className="w-4 h-4 text-blue-500"/>
                        <span className="text-xs font-mono uppercase tracking-tighter text-zinc-500">Core Identity</span>
                    </div>
                    <h1 className="text-3xl font-bold tracking-tight">Profile</h1>
                </div>

                <Button 
                    onClick={() => setIsEditDialogOpen(true)}
                    className="bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 text-white gap-2 px-4 shadow-none cursor-pointer transition-all"
                >
                    <Edit3 className="w-4 h-4"/> <span>Modify</span>
                </Button>
            </header>

            {error ? (
                <div className="flex flex-col items-center justify-center h-64 border border-red-900/20 bg-red-500/5 rounded-2xl p-6">
                    <AlertCircle className="w-10 h-10 text-red-500 mb-4"/>
                    <p className="text-zinc-500 text-sm font-mono mb-6">{error}</p>
                    <Button className="border-zinc-800 hover:bg-zinc-800 gap-2 cursor-pointer shadow-none" onClick={fetchProfileData} variant="outline">
                        <RefreshCw className="w-4 h-4"/> Re-sync
                    </Button>
                </div>
            ) : (
                <main className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    
                    {/* ---- Stats Architecture ---- */}
                    <div className="lg:col-span-1 space-y-6">
                        <div className="bg-zinc-900/40 border border-zinc-800/50 rounded-2xl p-6 relative overflow-hidden">
                            <div className="absolute inset-0 bg-gradient-to-br from-blue-600/5 to-transparent pointer-events-none" />
                            <div className="relative z-10">
                                <div className="flex items-center gap-4 mb-6">
                                    <div className="relative">
                                        <div className="w-16 h-16 rounded-2xl bg-blue-500/10 hover:bg-blue-600/20 border border-blue-500/20 hover:border-blue-500/40 flex items-center justify-center text-blue-500 font-bold text-2xl shadow-inner cursor-pointer">
                                            {profile?.full_name?.charAt(0) || "U"}{profile?.full_name?.split(" ")?.[1]?.charAt(0) || "U"}
                                        </div>
                                    </div>
                                    <div>
                                        <h2 className="text-xl font-bold text-white">{profile?.full_name}</h2>
                                        <p className="text-xs text-zinc-500 font-mono italic">@{profile?.user_name}</p>
                                    </div>
                                </div>
                                
                                <div className="space-y-4">
                                    <div className="flex justify-between items-center p-3 bg-zinc-900/60 hover:bg-zinc-900/90 border border-zinc-800/50 rounded-xl transition-all hover:border-amber-500/30">
                                        <div className="flex items-center gap-2">
                                            <Zap className="w-4 h-4 text-amber-500"/>
                                            <span className="text-[11px] uppercase font-bold text-zinc-500 tracking-wider">Learning Velocity</span>
                                        </div>
                                        <span className="font-mono text-amber-400 font-bold">{profile?.global_learning_velocity}</span>
                                    </div>
                                    <div className="flex justify-between items-center p-3 bg-zinc-900/60 hover:bg-zinc-900/90 border border-zinc-800/50 rounded-xl transition-all hover:border-purple-500/30">
                                        <div className="flex items-center gap-2">
                                            <Target className="w-4 h-4 text-purple-500"/>
                                            <span className="text-[11px] uppercase font-bold text-zinc-500 tracking-wider">Difficulty Band</span>
                                        </div>
                                        <span className="font-mono text-purple-400 font-bold">Lvl {profile?.preferred_difficulty_band}</span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            <div className="p-4 bg-zinc-900/50 border border-zinc-800/50 rounded-2xl hover:bg-zinc-900/90 transition-all group shadow-none">
                                
                                <div className="flex items-center justify-center gap-2 mb-3">
                                    <BarChart3 className="w-5 h-5 text-zinc-600 group-hover:text-blue-500 transition-colors"/>
                                    <p className="text-[10px] text-zinc-600 uppercase font-bold tracking-widest">
                                        Attempts
                                    </p>
                                </div>

                                <p className="text-2xl font-black text-zinc-200 text-center">
                                    {stats?.attempts || 0}
                                </p>
                            </div>

                            <div className="p-4 bg-zinc-900/50 border border-zinc-800/50 rounded-2xl hover:bg-zinc-900/90 transition-all group shadow-none">

                                <div className="flex items-center justify-center gap-2 mb-3">
                                    <Activity className="w-5 h-5 text-zinc-600 group-hover:text-emerald-500 transition-colors"/>
                                    <p className="text-[10px] text-zinc-600 uppercase font-bold tracking-widest">
                                        Enrollments
                                    </p>
                                </div>

                                <p className="text-2xl font-black text-zinc-200 text-center">
                                    {stats?.enrollments || 0}
                                </p>
                            </div>
                        </div>
                    </div>

                    {/* ---- Primary Data Display ---- */}
                    <div className="lg:col-span-2 space-y-6">
                        <div className="bg-zinc-900/40 border border-zinc-800/50 rounded-2xl p-8 relative overflow-hidden">
                            <div className="absolute top-0 right-0 p-8 opacity-5">
                                <Cpu className="w-16 h-16 text-white" />
                            </div>
                            
                            <h3 className="text-zinc-500 text-[10px] font-bold uppercase tracking-[0.3em] mb-8 relative z-10">System Access Protocols</h3>
                            
                            <div className="space-y-8 relative z-10">
                                <ProfileField icon={Mail} label="Transmission Endpoint" value={profile?.email}/>
                                <ProfileField 
                                    icon={Shield} 
                                    label="Role" 
                                    value={profile?.role} 
                                    badge={profile?.is_verified ? "Verified" : "Unverified"}
                                    badgeColor={profile?.is_verified ? "text-emerald-400" : "text-amber-400"}
                                />
                                <ProfileField 
                                    icon={Activity} 
                                    label="Neural State" 
                                    value={profile?.is_active ? "Active" : "Dormant"}
                                    badge={profile?.is_active ? "Active Link" : "Critical"}
                                    badgeColor={profile?.is_active ? "text-blue-400" : "text-red-400"}
                                />
                            </div>
                        </div>
                    </div>
                </main>
            )}

            {profile && (
                <EditProfileDialog 
                    isOpen={isEditDialogOpen} 
                    onOpenChange={setIsEditDialogOpen} 
                    onUpdate={handleUpdate} 
                    profile={profile}
                />
            )}
        </div>
    );
}

// ---- Sub-components ----

function ProfileField({ icon: Icon, label, value, badge, badgeColor }: any) {
    return (
        <div className="flex items-start justify-between border-b border-zinc-800/50 pb-6 last:border-0 last:pb-0">
            <div className="flex gap-4">
                <div className="p-2.5 rounded-xl bg-zinc-900 border border-zinc-800 text-zinc-500 shadow-none">
                    <Icon className="w-5 h-5"/>
                </div>
                <div>
                    <p className="text-[10px] font-bold text-zinc-600 uppercase tracking-wider mb-1">{label}</p>
                    <p className="text-zinc-200 font-medium font-mono">{value}</p>
                </div>
            </div>
            {badge && (
                <Badge variant="outline" className={`bg-zinc-950 border-zinc-800 ${badgeColor} font-mono px-3 py-1 text-[10px] uppercase tracking-tighter shadow-none`}>
                    {badge}
                </Badge>
            )}
        </div>
    );
}

function EditProfileDialog({ profile, isOpen, onOpenChange, onUpdate }: any) {
    const [isSaving, setIsSaving] = useState(false);
    const [formData, setFormData] = useState({
        full_name: profile.full_name,
        user_name: profile.user_name,
        preferred_difficulty_band: profile.preferred_difficulty_band
    });

    const handleSave = async () => {
        try {
            setIsSaving(true);
            const updated = await profileService.updateMyProfile(formData);
            onUpdate(updated);
            onOpenChange(false);
        } catch (err) {
            console.error("Protocol Update Failure:", err);
        } finally {
            setIsSaving(false);
        }
    };

    return (
        <Dialog open={isOpen} onOpenChange={onOpenChange}>
            <DialogContent className="bg-zinc-950/90 backdrop-blur-2xl border-zinc-900/50 text-white sm:max-w-sm overflow-hidden rounded-2xl p-0 [&>button]:hidden shadow-none">
                <DialogClose asChild>
                    <button className="absolute right-5 top-5 z-50 p-2 text-zinc-500 hover:text-red-500 transition-all cursor-pointer group">
                        <X className="h-4 w-4 group-hover:rotate-90 transition-transform"/>
                    </button>
                </DialogClose>

                <div className="absolute inset-0 bg-gradient-to-b from-blue-600/10 to-transparent pointer-events-none h-32" />

                <DialogHeader className="px-6 pt-8 pb-3 relative z-10">
                    <div className="flex items-center gap-3">
                        <div className="p-2 rounded-xl bg-blue-600/10 border border-blue-500/20 shadow-none">
                            <Key className="h-4 w-4 text-blue-500"/>
                        </div>
                        <DialogTitle className="text-lg font-black tracking-tight uppercase text-zinc-100">Update User Profile</DialogTitle>
                    </div>
                    <DialogDescription className="text-zinc-500 text-[10px] font-mono ml-1 mt-1.5 tracking-widest">
                        Update your personal information and preferences.
                    </DialogDescription>
                </DialogHeader>

                <div className="px-6 pb-6 space-y-5 relative z-10">
                    <div className="space-y-1.5">
                        <Label className="text-zinc-500 text-[9px] font-bold uppercase tracking-wider ml-1 mb-2">Full Name</Label>
                        <Input 
                            className="bg-zinc-900/50 border-zinc-800 h-10 text-sm rounded-xl focus:ring-1 focus:ring-blue-600/40 transition-all shadow-none" 
                            value={formData.full_name}
                            onChange={(e) => setFormData({...formData, full_name: e.target.value})}
                        />
                    </div>

                    <div className="space-y-1.5">
                        <Label className="text-zinc-500 text-[9px] font-bold uppercase tracking-wider ml-1 mb-2">User Name</Label>
                        <Input 
                            className="bg-zinc-900/50 border-zinc-800 h-10 text-sm rounded-xl focus:ring-1 focus:ring-blue-600/40 transition-all font-mono shadow-none" 
                            value={formData.user_name}
                            onChange={(e) => setFormData({...formData, user_name: e.target.value})}
                        />
                    </div>

                    <div className="pt-2 flex gap-2">
                        <Button 
                            variant="ghost"
                            onClick={() => onOpenChange(false)}
                            className="flex-1 h-10 text-xs bg-zinc-900/50 hover:bg-red-500/10 hover:text-red-500 border border-zinc-800 rounded-xl font-bold cursor-pointer transition-all shadow-none"
                        >
                            Abort
                        </Button>
                        <Button 
                            className="flex-1 h-10 text-xs bg-blue-600 hover:bg-blue-500 text-white font-bold rounded-xl shadow-none cursor-pointer transition-all" 
                            disabled={isSaving}
                            onClick={handleSave}
                        >
                            {isSaving ? <Loader2 className="h-3 w-3 animate-spin"/> : "Commit"}
                        </Button>
                    </div>
                </div>
            </DialogContent>
        </Dialog>
    );
}