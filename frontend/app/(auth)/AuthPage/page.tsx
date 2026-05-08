"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { authService } from "@/services/auth.service";
import { Loader2, Lock, Mail, ShieldCheck, Sparkles, UserPlus, User, AtSign, ArrowLeft, AlertCircle, CheckCircle2 } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";

const APP_NAME = "ExamAI";

export default function AuthPage() {
  const router = useRouter();

  const [isLogin, setIsLogin] = useState(true);
  const [isReset, setIsReset] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  
  const [formData, setFormData] = useState({
    full_name: "",
    user_name: "",
    email: "",
    password: ""
  });

  const switchToReset = () => { setIsReset(true); setIsLogin(false); setError(null); setSuccess(null); };
  const switchToLogin = () => { setIsReset(false); setIsLogin(true); setError(null); setSuccess(null); };
  const switchToRegister = () => { setIsReset(false); setIsLogin(false); setError(null); setSuccess(null); };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData(prev => ({ ...prev, [e.target.name]: e.target.value }));
    if (error) setError(null);
    if (success) setSuccess(null);
  };

  // ---- Form Submission ----
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      if (isReset) {
        const res = await authService.resetPassword(formData.email);
        setSuccess(res.message || "Reset link sent successfully!");
      } else if (!isLogin) {
        // ---- REGISTER FLOW ----
        await authService.register(formData);
        setSuccess("Account created! You need to verify your email before logging in.");
        
        // ---- CLEAR PASSWORD AFTER REGISTRATION ----
        setFormData(prev => ({ ...prev, password: "" }));
        
        // Delay slightly for UX then switch
        setTimeout(() => setIsLogin(true), 2000);
      } else {
        // ---- LOGIN FLOW ----
        const data = await authService.login(formData.email, formData.password);
        if (data?.access_token) {
          localStorage.setItem("token", data.access_token);
          setSuccess("Login successful! Redirecting...");
          setTimeout(() => router.push("/dashboard"), 1500);
        }
      }
    } catch (err: any) {
      setError(err.message || "Something went wrong.");
    } finally {
      setLoading(false);
    }
  };

  const inputClasses = "pl-10 h-12 bg-zinc-950 border-zinc-800/50 text-zinc-100 placeholder:text-white/20 focus:border-blue-900/50 autofill:shadow-[inset_0_0_0px_1000px_rgb(9,9,11)] [-webkit-text-fill-color:white] transition-colors";
  const smallInputClasses = "pl-9 h-11 bg-zinc-950 border-zinc-800/50 text-zinc-100 text-sm placeholder:text-white/20 focus:border-blue-900/50 autofill:shadow-[inset_0_0_0px_1000px_rgb(9,9,11)] [-webkit-text-fill-color:white] transition-colors";

  return (
    <div className="relative min-h-screen w-full flex items-center justify-center bg-zinc-950 overflow-hidden px-4 py-10 md:py-24 antialiased">
      
      <div className="absolute inset-0 z-0">
        <div className="absolute inset-0 bg-gradient-to-tr from-blue-600/15 via-transparent to-indigo-600/15" />
        <div className="absolute inset-0 bg-gradient-to-bl from-indigo-600/10 via-transparent to-blue-600/10" />
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:44px_44px] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_50%,#000_70%,transparent_100%)]" />
      </div>

      <div className="absolute top-1/4 left-1/4 w-[500px] h-[500px] bg-blue-600/20 blur-[120px] rounded-full animate-pulse pointer-events-none" />
      <div className="absolute bottom-1/4 right-1/4 w-[500px] h-[500px] bg-indigo-600/20 blur-[120px] rounded-full animate-pulse pointer-events-none [animation-delay:2s]" />

      <div className="relative z-10 w-full max-w-[440px]">
        <div className="flex flex-col items-center mb-8 space-y-4">
          <div className="group relative flex h-14 w-14 items-center justify-center rounded-2xl bg-zinc-900 border border-zinc-800 shadow-inner">
            <div className="absolute inset-0 rounded-2xl bg-gradient-to-tr from-blue-700 to-indigo-700 opacity-20 blur-sm group-hover:opacity-40 transition-opacity" />
            <Sparkles className="h-7 w-7 text-white relative z-10" />
          </div>
          <div className="text-center">
            <h1 className="text-3xl font-bold tracking-tight text-white">{APP_NAME}</h1>
            <p className="text-sm text-zinc-600 mt-1 uppercase tracking-widest font-medium">Smart Learning Platform</p>
          </div>
        </div>

        <Card className="border border-white/5 bg-zinc-900/60 backdrop-blur-2xl shadow-[0_0_50px_-12px_rgba(0,0,0,0.8)] rounded-3xl overflow-hidden">
          <CardHeader className="pb-4 pt-8">
            <CardTitle className="text-xl font-medium text-white flex items-center gap-2">
              {isReset ? (
                <button type="button" onClick={switchToLogin} className="flex items-center gap-2 hover:text-blue-400 transition-colors">
                  <ArrowLeft className="w-5 h-5" /> Reset Password
                </button>
              ) : isLogin ? (
                <><ShieldCheck className="w-5 h-5 text-blue-500" /> Secure Access</>
              ) : (
                <><UserPlus className="w-5 h-5 text-blue-500" /> Create Account</>
              )}
            </CardTitle>
          </CardHeader>

          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-5">
              {error && (
                <div className="flex items-center gap-2 p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-xs animate-in fade-in slide-in-from-top-1">
                  <AlertCircle className="h-4 w-4 shrink-0" />
                  <p>{error}</p>
                </div>
              )}

              {success && (
                <div className="flex items-center gap-2 p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs animate-in fade-in slide-in-from-top-1">
                  <CheckCircle2 className="h-4 w-4 shrink-0" />
                  <p>{success}</p>
                </div>
              )}

              {!isLogin && !isReset && (
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label className="text-zinc-500 text-xs ml-1">Full Name</Label>
                    <div className="relative">
                      <User className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-zinc-600" />
                      <Input name="full_name" required value={formData.full_name} onChange={handleChange} placeholder="John Doe" className={smallInputClasses} />
                    </div>
                  </div>
                  <div className="space-y-2">
                    <Label className="text-zinc-500 text-xs ml-1">Username</Label>
                    <div className="relative">
                      <AtSign className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-zinc-600" />
                      <Input name="user_name" required value={formData.user_name} onChange={handleChange} placeholder="johndoe" className={smallInputClasses} />
                    </div>
                  </div>
                </div>
              )}

              <div className="space-y-2">
                <Label className="text-zinc-500 text-xs ml-1">Email</Label>
                <div className="relative group">
                  <Mail className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-zinc-600" />
                  <Input name="email" required type="email" value={formData.email} onChange={handleChange} placeholder="name@company.com" className={inputClasses} />
                </div>
              </div>

              {!isReset && (
                <div className="space-y-2">
                  <div className="flex items-center justify-between px-1">
                    <Label className="text-zinc-500 text-xs">Password</Label>
                    {isLogin && (
                      <button type="button" onClick={switchToReset} className="text-[11px] text-blue-500/80 hover:text-blue-400 transition-colors font-medium">
                        Forgot password?
                      </button>
                    )}
                  </div>
                  <div className="relative group">
                    <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-zinc-600" />
                    <Input name="password" required type="password" value={formData.password} onChange={handleChange} placeholder="••••••••" className={inputClasses} />
                  </div>
                </div>
              )}

              <Button type="submit" disabled={loading} className="w-full h-12 bg-blue-950/80 hover:bg-blue-900 text-blue-100 border border-blue-500/30 font-semibold shadow-2xl transition-all active:scale-[0.98]">
                {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : (isReset ? "Reset Password" : (isLogin ? "Sign In" : "Get Started"))}
              </Button>

              {!isReset && (
                <div className="pt-2 text-center border-t border-white/5">
                  <button type="button" onClick={isLogin ? switchToRegister : switchToLogin} className="text-sm text-zinc-600 hover:text-white transition-colors">
                    {isLogin ? "Don't have an account? Create one" : "Already have an account? Sign in"}
                  </button>
                </div>
              )}
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}