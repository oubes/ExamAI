"use client";

import { useState, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { authService } from "@/services/auth.service";
import { Loader2, Lock, AlertCircle, ArrowLeft, Eye, EyeOff } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";

import {
  AuthLogo,
  AuthStatusMessages,
  AuthBackground,
} from "@/components/auth/auth-elements";

const APP_NAME = "ExamAI";

export default function ResetPasswordPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const token = searchParams.get("token");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [isTokenValid, setIsTokenValid] = useState<boolean>(true);
  
  // ---- Visibility States ----
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const [formData, setFormData] = useState({
    password: "",
    confirmPassword: "",
  });

  useEffect(() => {
    const handledToken = authService.handleResetRedirect(token);

    if (!handledToken) {
      setError("Reset token is missing or invalid.");
      setIsTokenValid(false);
    }
  }, [token]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData((prev) => ({
      ...prev,
      [e.target.name]: e.target.value,
    }));

    if (error) setError(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (formData.password !== formData.confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      await authService.confirmResetPassword(
        token!,
        formData.password
      );

      setSuccess("Password updated! Redirecting to login...");

      setTimeout(() => {
        router.push("/AuthPage?reset=1");
      }, 2000);
    } catch (err: any) {
      setError(err.message || "Failed to reset password.");
      setLoading(false);
    }
  };

  const inputClasses = `
    pl-10 pr-10 h-12 bg-zinc-950 border-zinc-800/50 text-zinc-100 placeholder:text-white/20 
    focus:border-blue-900/50 transition-colors
    autofill:shadow-[0_0_0_30px_#09090b_inset] 
    [-webkit-text-fill-color:white]
  `;

  return (
    <div className="relative min-h-screen w-full flex items-center justify-center bg-zinc-950 overflow-hidden px-4 py-10 antialiased">
      <AuthBackground />

      <div className="relative z-10 w-full max-w-[440px]">
        <AuthLogo appName={APP_NAME} />

        <Card className="border border-white/5 bg-zinc-900/60 backdrop-blur-2xl rounded-3xl overflow-hidden shadow-2xl">
          <CardHeader
            className={`pb-0 ${!isTokenValid ? "pt-2" : "pt-8"}`}
          >
            <CardTitle className="text-xl font-medium text-white flex items-center gap-2.5">
              {!isTokenValid && (
                <span className="flex h-2 w-2 rounded-full bg-red-900 shadow-[0_0_8px_rgba(127,29,29,0.4)]" />
              )}
              {isTokenValid ? "New Password" : "Invalid Link"}
            </CardTitle>
          </CardHeader>

          <CardContent className={!isTokenValid ? "pt-0 mt-0" : ""}>
            {!isTokenValid ? (
              <div className="space-y-4 -mt-1">
                <div className="flex flex-col items-center justify-center pt-0 pb-1 px-2 text-center space-y-3">
                  <div className="h-12 w-12 rounded-full bg-red-500/10 flex items-center justify-center">
                    <AlertCircle className="h-6 w-6 text-red-500" />
                  </div>

                  <div className="space-y-1">
                    <h3 className="text-zinc-200 font-medium text-sm">
                      Reset Link Error
                    </h3>
                    <p className="text-[11px] text-zinc-500 leading-tight">
                      The password reset link is invalid, expired, or has already been used.
                    </p>
                  </div>
                </div>

                <Button
                  onClick={() => router.push("/AuthPage")}
                  className="w-full h-10 bg-zinc-900 text-zinc-500 hover:bg-zinc-800 hover:text-zinc-300 font-bold rounded-xl transition-all duration-200 cursor-pointer border border-white/5"
                >
                  <ArrowLeft className="w-4 h-4 mr-2" />
                  Back to Login
                </Button>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="space-y-5">
                <AuthStatusMessages error={error} success={success} />

                <div className="space-y-4">
                  <div className="space-y-2">
                    <Label className="text-zinc-500 text-xs ml-1">
                      New Password
                    </Label>

                    <div className="relative group">
                      <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-zinc-600 z-10" />

                      <Input
                        name="password"
                        required
                        type={showPassword ? "text" : "password"}
                        value={formData.password}
                        onChange={handleChange}
                        placeholder="••••••••"
                        className={`${inputClasses} placeholder:opacity-30`} 
                      />
                      <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-zinc-600 hover:text-zinc-400 transition-colors cursor-pointer z-20"
                      >
                        {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                      </button>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label className="text-zinc-500 text-xs ml-1">
                      Confirm New Password
                    </Label>

                    <div className="relative group">
                      <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-zinc-600 z-10" />

                      <Input
                        name="confirmPassword"
                        required
                        type={showConfirmPassword ? "text" : "password"}
                        value={formData.confirmPassword}
                        onChange={handleChange}
                        placeholder="••••••••"
                        className={`${inputClasses} placeholder:opacity-30`}
                      />
                      <button
                        type="button"
                        onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-zinc-600 hover:text-zinc-400 transition-colors cursor-pointer z-20"
                      >
                        {showConfirmPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                      </button>
                    </div>
                  </div>
                </div>

                <Button
                  type="submit"
                  disabled={loading || !!success}
                  className="w-full h-12 bg-blue-900/20 hover:bg-blue-900/40 text-blue-700 hover:text-blue-500 border border-blue-900/30 hover:border-blue-800 font-semibold transition-all duration-200 active:scale-[0.98] cursor-pointer disabled:cursor-not-allowed"
                >
                  {loading ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    "Update Password"
                  )}
                </Button>

                <div className="pt-2 text-center border-t border-white/5">
                  <button
                    type="button"
                    onClick={() => router.push("/AuthPage")}
                    className="text-sm text-zinc-600 hover:text-zinc-400 transition-colors cursor-pointer"
                  >
                    Return to Sign In
                  </button>
                </div>
              </form>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}