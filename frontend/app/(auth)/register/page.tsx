"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { authService } from "@/services/auth.service";
import { Loader2, Lock, Mail, Sparkles, User } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";

const APP_NAME = "ExamAI";

export default function RegisterPage() {
  const router = useRouter();

  const [full_name, setFullName] = useState("");
  const [user_name, setUserName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [loading, setLoading] = useState(false);

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      await authService.register({
        full_name,
        user_name,
        email,
        password,
      });

      router.push("/login");
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative min-h-screen w-full flex items-center justify-center bg-zinc-950 px-4 py-20 md:py-24 antialiased">

      {/* Background */}
      <div className="absolute inset-0 z-0">
        <div className="absolute inset-0 bg-gradient-to-tr from-purple-500/5 via-transparent to-cyan-500/5" />
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#8080800a_1px,transparent_1px),linear-gradient(to_bottom,#8080800a_1px,transparent_1px)] bg-[size:44px_44px]" />
      </div>

      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[400px] bg-purple-600/10 blur-[120px] rounded-full" />

      {/* MAIN WRAPPER (FIXED) */}
      <div className="relative z-10 w-full max-w-[420px] flex flex-col items-center gap-8">

        {/* BRAND (SAME HEIGHT) */}
        <div className="h-[140px] flex flex-col items-center justify-center space-y-4">

          <div className="relative flex h-14 w-14 items-center justify-center rounded-2xl bg-zinc-900 border border-zinc-800">
            <div className="absolute inset-0 rounded-2xl bg-gradient-to-tr from-purple-500 to-cyan-500 opacity-20 blur-sm" />
            <Sparkles className="h-7 w-7 text-white relative z-10" />
          </div>

          <div className="text-center">
            <h1 className="text-3xl font-bold text-white">{APP_NAME}</h1>
            <button
              onClick={() => router.push("/login")}
              className="text-sm text-zinc-500 uppercase tracking-widest hover:text-purple-400"
            >
              Already have account? Sign in
            </button>
          </div>

        </div>

        {/* CARD */}
        <Card className="w-full border border-white/10 bg-zinc-900/40 backdrop-blur-xl rounded-3xl">

          <CardHeader className="pb-4 pt-8">
            <CardTitle className="text-xl text-white flex items-center gap-2">
              <User className="w-5 h-5 text-purple-400" />
              Create Account
            </CardTitle>
          </CardHeader>

          <CardContent>
            <form onSubmit={handleRegister} className="space-y-6">

              <Input value={full_name} onChange={(e)=>setFullName(e.target.value)} placeholder="Full Name" />
              <Input value={user_name} onChange={(e)=>setUserName(e.target.value)} placeholder="Username" />
              <Input value={email} onChange={(e)=>setEmail(e.target.value)} placeholder="Email" />
              <Input type="password" value={password} onChange={(e)=>setPassword(e.target.value)} placeholder="Password" />

              <Button className="w-full h-12 bg-white text-black font-semibold">
                {loading ? <Loader2 className="animate-spin h-4 w-4" /> : "Create account"}
              </Button>

            </form>
          </CardContent>

        </Card>

      </div>
    </div>
  );
}