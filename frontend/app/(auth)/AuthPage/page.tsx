"use client";

import { useState, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { authService } from "@/services/auth.service";
import { 
  Loader2, Lock, Mail, ShieldCheck, UserPlus, 
  User, AtSign, ArrowLeft, Eye, EyeOff 
} from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";

import { AuthLogo, AuthStatusMessages, AuthBackground } from "@/components/auth/auth-elements";

const APP_NAME = "ExamAI";

export default function AuthPage() {
  const router = useRouter();
  const searchParams = useSearchParams();

  const [isLogin, setIsLogin] = useState(true);
  const [isReset, setIsReset] = useState(false);
  const [loading, setLoading] = useState(false);
  const [checkingAuth, setCheckingAuth] = useState(true);
  const [showPassword, setShowPassword] = useState(false); // ---- Password Visibility State ----
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  
  const [formData, setFormData] = useState({
    full_name: "",
    user_name: "",
    email: "",
    password: ""
  });

  // ---- Auth Check ----
  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (token) {
      router.replace("/dashboard");
    } else {
      setCheckingAuth(false);
    }
  }, [router]);

  // ---- URL Params Check ----
  useEffect(() => {
    const verified = searchParams.get("verified");
    const resetSuccess = searchParams.get("reset");

    if (verified === "1") {
      setSuccess("Email verified successfully!");
      setIsLogin(true);
      window.history.replaceState(null, '', window.location.pathname);
    }
    if (resetSuccess === "1") {
      setSuccess("Password has been reset successfully.");
      setIsLogin(true);
      window.history.replaceState(null, '', window.location.pathname);
    }
  }, [searchParams]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData(prev => ({ ...prev, [e.target.name]: e.target.value }));
    if (error) setError(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      if (isReset) {
        const res = await authService.resetPassword(formData.email);
        setSuccess(res.message || "Reset link sent!");
        setLoading(false);
        return;
      }

      if (!isLogin) {
        const res = await authService.register(formData);
        setSuccess(res.message || "Account created. Check email.");
        setLoading(false);
        setTimeout(() => setIsLogin(true), 3000);
        return;
      }

      const response = await authService.login(formData.email, formData.password);
      const authData = response?.data || response;

      if (authData && authData.access_token) {
        localStorage.setItem("access_token", authData.access_token);
        if (authData.refresh_token) {
          localStorage.setItem("refresh_token", authData.refresh_token);
        }
        setSuccess("Success! Redirecting...");
        setTimeout(() => router.push("/dashboard"), 800);
      } else {
        setError(authData?.detail || "Unexpected response from server.");
        setLoading(false);
      }
    } catch (err: any) {
      const msg = err?.response?.data?.detail || err?.message || "Auth failed.";
      setError(msg);
      setLoading(false);
    }
  };

  if (checkingAuth) {
    return (
      <div className="min-h-screen w-full flex items-center justify-center bg-zinc-950">
        <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
      </div>
    );
  }

  // ---- Styles Constants ----
  const inputClasses = `
    pl-10 pr-10 h-12 bg-zinc-950 border-zinc-800/50 text-zinc-100 placeholder:text-white/20 
    focus:border-blue-900/50 transition-colors
    autofill:shadow-[0_0_0_30px_#09090b_inset] 
    autofill:text-zinc-100
    [-webkit-text-fill-color:white]
  `;

  const smallInputClasses = `
    pl-9 h-11 bg-zinc-950 border-zinc-800/50 text-zinc-100 text-sm placeholder:text-white/20 
    focus:border-blue-900/50 transition-colors
    autofill:shadow-[0_0_0_30px_#09090b_inset] 
    [-webkit-text-fill-color:white]
  `;

  return (
    <div className="relative min-h-screen w-full flex items-center justify-center bg-zinc-950 overflow-hidden px-4 py-10 md:py-24 antialiased">
      <AuthBackground />

      <div className="relative z-10 w-full max-w-[440px]">
        <AuthLogo appName={APP_NAME} />

        <Card className="border border-white/5 bg-zinc-900/60 backdrop-blur-2xl rounded-3xl overflow-hidden shadow-2xl">
          <CardHeader className="pb-4 pt-8">
            <CardTitle className="text-xl font-medium text-white flex items-center gap-2">
              {isReset ? (
                <button 
                  type="button" 
                  onClick={() => { setIsReset(false); setIsLogin(true); setError(null); }} 
                  className="flex items-center gap-2 hover:text-blue-400 transition-colors cursor-pointer"
                >
                  <ArrowLeft className="w-5 h-5" /> Reset Password
                </button>
              ) : isLogin ? (
                <><ShieldCheck className="w-5 h-5 text-blue-500" /> Secure Login</>
              ) : (
                <><UserPlus className="w-5 h-5 text-blue-500" /> Create Account</>
              )}
            </CardTitle>
          </CardHeader>

          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-5">
              <AuthStatusMessages error={error} success={success} />

              {!isLogin && !isReset && (
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label className="text-zinc-500 text-xs ml-1">Full Name</Label>
                    <div className="relative">
                      <User className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-zinc-600 z-10" />
                      <Input name="full_name" required value={formData.full_name} onChange={handleChange} className={smallInputClasses} />
                    </div>
                  </div>
                  <div className="space-y-2">
                    <Label className="text-zinc-500 text-xs ml-1">Username</Label>
                    <div className="relative">
                      <AtSign className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-zinc-600 z-10" />
                      <Input name="user_name" required value={formData.user_name} onChange={handleChange} className={smallInputClasses} />
                    </div>
                  </div>
                </div>
              )}

              <div className="space-y-2">
                <Label className="text-zinc-500 text-xs ml-1">Email</Label>
                <div className="relative group">
                  <Mail className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-zinc-600 z-10" />
                  <Input name="email" required type="email" value={formData.email} onChange={handleChange} placeholder="name@company.com" className={inputClasses} />
                </div>
              </div>

              {!isReset && (
                <div className="space-y-2">
                  <div className="flex items-center justify-between px-1">
                    <Label className="text-zinc-500 text-xs">Password</Label>
                    {isLogin && (
                      <button 
                        type="button" 
                        onClick={() => { setIsReset(true); setIsLogin(false); setError(null); }} 
                        className="text-[11px] text-blue-500/80 hover:text-blue-400 font-medium cursor-pointer"
                      >
                        Forgot password?
                      </button>
                    )}
                  </div>
                  <div className="relative group">
                    <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-zinc-600 z-10" />
                    <Input 
                      name="password" 
                      required 
                      type={showPassword ? "text" : "password"} 
                      value={formData.password} 
                      onChange={handleChange} 
                      placeholder="••••••••" 
                      className={inputClasses} 
                    />
                    {/* ---- Toggle Visibility Button ---- */}
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-zinc-600 hover:text-zinc-400 transition-colors cursor-pointer z-20"
                    >
                      {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </button>
                  </div>
                </div>
              )}

              <Button 
                type="submit" 
                disabled={loading} 
                className="w-full h-12 bg-blue-950/80 hover:bg-blue-900 text-blue-100 border border-blue-500/30 font-semibold transition-all active:scale-[0.98] cursor-pointer disabled:cursor-not-allowed"
              >
                {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : (isReset ? "Reset Password" : (isLogin ? "Sign In" : "Sign Up"))}
              </Button>

              {!isReset && (
                <div className="pt-2 text-center border-t border-white/5">
                  <button 
                    type="button" 
                    onClick={() => { setIsLogin(!isLogin); setError(null); }} 
                    className="text-sm text-zinc-600 hover:text-white transition-colors cursor-pointer"
                  >
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