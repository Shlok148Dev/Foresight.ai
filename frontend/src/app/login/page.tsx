"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { motion } from "framer-motion";
import { Eye, ArrowRight } from "lucide-react";
import { useAuth } from "@/hooks/useAuth";

export default function LoginPage() {
  const router = useRouter();
  const { login, isLoading, error, clearError } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await login(email, password);
      router.push("/dashboard");
    } catch {
      /* error is already in store */
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-md md:p-lg bg-background relative overflow-hidden font-body-md selection:bg-primary-container selection:text-on-primary-container">
      {/* Decorative Background Elements */}
      <div className="absolute top-0 left-1/4 w-96 h-96 bg-primary/10 rounded-full blur-[100px] pointer-events-none"></div>
      <div className="absolute bottom-0 right-1/4 w-[500px] h-[500px] bg-secondary/10 rounded-full blur-[120px] pointer-events-none"></div>
      
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-[480px] glass-panel rounded-xl p-xl shadow-[0_10px_30px_rgba(0,0,0,0.5)] relative z-10"
      >
        {/* Header */}
        <div className="text-center mb-xl">
          <Link href="/" className="inline-flex items-center justify-center gap-2 mb-sm hover:scale-105 transition-transform">
            <Eye className="w-8 h-8 text-primary" />
            <h1 className="font-headline-lg text-3xl font-bold text-primary">Foresight</h1>
          </Link>
          <h2 className="font-headline-md text-2xl font-bold text-on-surface">Welcome back</h2>
          <p className="font-body-md text-on-surface-variant mt-sm">Sign in to your predictive intelligence account.</p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-lg">
          <div className="space-y-md">
            {/* Email */}
            <div>
              <label className="block font-body-sm text-sm font-semibold text-on-surface-variant mb-xs" htmlFor="email">Email</label>
              <input 
                className="w-full bg-surface border border-outline-variant rounded-lg px-md py-sm font-body-md text-on-surface placeholder:text-on-surface-variant/50 focus:border-primary focus:ring-1 focus:ring-primary focus:outline-none transition-colors" 
                id="email" 
                type="email"
                value={email}
                onChange={(e) => { setEmail(e.target.value); clearError(); }}
                placeholder="jane@example.com"
                required 
              />
            </div>
            {/* Password */}
            <div>
              <label className="block font-body-sm text-sm font-semibold text-on-surface-variant mb-xs" htmlFor="password">Password</label>
              <input 
                className="w-full bg-surface border border-outline-variant rounded-lg px-md py-sm font-body-md text-on-surface placeholder:text-on-surface-variant/50 focus:border-primary focus:ring-1 focus:ring-primary focus:outline-none transition-colors" 
                id="password" 
                type="password"
                value={password}
                onChange={(e) => { setPassword(e.target.value); clearError(); }}
                placeholder="••••••••"
                required 
              />
            </div>
          </div>

          {error && (
            <motion.div
              initial={{ opacity: 0, y: -4 }}
              animate={{ opacity: 1, y: 0 }}
              className="rounded-lg border border-error/20 bg-error/10 px-4 py-3 text-sm text-error"
            >
              {error}
            </motion.div>
          )}

          {/* Primary Action */}
          <button 
            type="submit"
            disabled={isLoading}
            className="w-full bg-primary-container text-background font-bold text-lg py-sm px-lg rounded-lg hover:scale-[1.02] hover:brightness-110 active:scale-[0.98] transition-all duration-200 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? "Signing In..." : "Sign In"}
            {!isLoading && <ArrowRight className="w-5 h-5" />}
          </button>

          {/* Divider */}
          <div className="relative flex items-center py-md">
            <div className="flex-grow border-t border-outline-variant"></div>
            <span className="flex-shrink-0 mx-md text-on-surface-variant font-label-caps text-xs font-bold tracking-wider">OR CONTINUE WITH</span>
            <div className="flex-grow border-t border-outline-variant"></div>
          </div>

          {/* Social Actions */}
          <div className="grid grid-cols-2 gap-md">
            <button type="button" className="flex items-center justify-center gap-2 bg-transparent border border-outline-variant rounded-lg py-sm px-md text-on-surface font-body-sm hover:scale-[1.02] hover:bg-surface-variant transition-all duration-200">
              <img alt="Google" className="w-5 h-5" src="https://lh3.googleusercontent.com/aida-public/AB6AXuBpnavtCuM37pwVAabBa5wYJc-DFyCii9ODQZKv_GvSCAOCg9u5YTRpBmM16Zix_Srs2c95y_1qAI0m0rfqe7qvVyN1ovPSdHH-ZWw5CmUwBqi3pFJ4pKCC5enSRW5oDt0AFLnlG64EojaA0pSAz166EUQZZbjvWkMqpj10dQmZxviIu820-O_svKNu-QG9oTZ8jGKjyjqaymkEzttzLQ8C_0y2uF33x06LeZvk6YXPSD4Jh6Hq5FAyF2DHBSEeU0use0awlXvwVo4"/>
              Google
            </button>
            <button type="button" className="flex items-center justify-center gap-2 bg-transparent border border-outline-variant rounded-lg py-sm px-md text-on-surface font-body-sm hover:scale-[1.02] hover:bg-surface-variant transition-all duration-200">
              <img alt="GitHub" className="w-5 h-5 filter invert" src="https://lh3.googleusercontent.com/aida-public/AB6AXuASlQbUsBixh47gLwd6maw-TxSXxIRwffxQe_m1smyQLlTXImzoZp3LSWcgsen3UAUHuti0HQotzHoPNnZkAGvgsaKigGmQmdrDH1k7PVP_J3MoiUmqevHJimaPiyEm7yt6DO8VA2uM76ktjxqBu-8moUPYqq-_nw21QkM8mA78k5n1YXWzX5YgxtHIA0PTSVFGZ5dBYKspucm9u2cunbjYXzUFnyDFjZ6tr8rK9m4u0FrTzrWCA3E1B_bxG9zZPYGPU6KOpdKVFg0"/>
              GitHub
            </button>
          </div>

          {/* Sign Up Link */}
          <p className="text-center font-body-sm text-on-surface-variant pt-sm">
            Don't have an account?{" "}
            <Link href="/signup" className="text-primary hover:underline font-semibold transition-colors duration-200">Create one</Link>
          </p>
        </form>
      </motion.div>
    </div>
  );
}
