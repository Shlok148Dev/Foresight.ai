"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { motion } from "framer-motion";
import { Eye, ArrowRight } from "lucide-react";
import { useAuth } from "@/hooks/useAuth";

export default function SignupPage() {
  const router = useRouter();
  const { register, isLoading, error, clearError } = useAuth();
  const [form, setForm] = useState({
    email: "",
    password: "",
    confirmPassword: "",
    username: "",
    full_name: "",
    terms: false,
  });

  const update = (field: string, value: string | boolean) => {
    setForm((prev) => ({ ...prev, [field]: value }));
    clearError();
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (form.password !== form.confirmPassword) {
      // In a real app we'd set a local error state for validation
      return;
    }
    if (!form.terms) return;
    
    try {
      await register(form.email, form.password, form.username, form.full_name);
      router.push("/dashboard");
    } catch {
      /* error is in store */
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
        className="w-full max-w-[480px] glass-panel rounded-xl p-xl shadow-[0_10px_30px_rgba(0,0,0,0.5)] relative z-10 my-8"
      >
        {/* Header */}
        <div className="text-center mb-xl">
          <Link href="/" className="inline-flex items-center justify-center gap-2 mb-sm hover:scale-105 transition-transform">
            <Eye className="w-8 h-8 text-primary" />
            <h1 className="font-headline-lg text-3xl font-bold text-primary">Foresight</h1>
          </Link>
          <h2 className="font-headline-md text-2xl font-bold text-on-surface">Create your account</h2>
          <p className="font-body-md text-on-surface-variant mt-sm">Join the predictive intelligence platform.</p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-lg">
          <div className="space-y-md">
            {/* Full Name */}
            <div>
              <label className="block font-body-sm text-sm font-semibold text-on-surface-variant mb-xs" htmlFor="fullName">Full name</label>
              <input 
                className="w-full bg-surface border border-outline-variant rounded-lg px-md py-sm font-body-md text-on-surface placeholder:text-on-surface-variant/50 focus:border-primary focus:ring-1 focus:ring-primary focus:outline-none transition-colors" 
                id="fullName" 
                type="text"
                value={form.full_name}
                onChange={(e) => update("full_name", e.target.value)}
                placeholder="Jane Doe"
              />
            </div>

            {/* Username */}
            <div>
              <label className="block font-body-sm text-sm font-semibold text-on-surface-variant mb-xs" htmlFor="username">Username</label>
              <input 
                className="w-full bg-surface border border-outline-variant rounded-lg px-md py-sm font-body-md text-on-surface placeholder:text-on-surface-variant/50 focus:border-primary focus:ring-1 focus:ring-primary focus:outline-none transition-colors" 
                id="username" 
                type="text"
                value={form.username}
                onChange={(e) => update("username", e.target.value)}
                placeholder="janedoe"
                required
              />
            </div>

            {/* Email */}
            <div>
              <label className="block font-body-sm text-sm font-semibold text-on-surface-variant mb-xs" htmlFor="email">Email</label>
              <input 
                className="w-full bg-surface border border-outline-variant rounded-lg px-md py-sm font-body-md text-on-surface placeholder:text-on-surface-variant/50 focus:border-primary focus:ring-1 focus:ring-primary focus:outline-none transition-colors" 
                id="email" 
                type="email"
                value={form.email}
                onChange={(e) => update("email", e.target.value)}
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
                value={form.password}
                onChange={(e) => update("password", e.target.value)}
                placeholder="••••••••"
                required
              />
            </div>

            {/* Confirm Password */}
            <div>
              <label className="block font-body-sm text-sm font-semibold text-on-surface-variant mb-xs" htmlFor="confirmPassword">Confirm password</label>
              <input 
                className="w-full bg-surface border border-outline-variant rounded-lg px-md py-sm font-body-md text-on-surface placeholder:text-on-surface-variant/50 focus:border-primary focus:ring-1 focus:ring-primary focus:outline-none transition-colors" 
                id="confirmPassword" 
                type="password"
                value={form.confirmPassword}
                onChange={(e) => update("confirmPassword", e.target.value)}
                placeholder="••••••••"
                required
              />
            </div>
          </div>

          {/* Terms Checkbox */}
          <div className="flex items-start gap-sm">
            <div className="flex items-center h-5">
              <input 
                className="w-4 h-4 bg-surface border-outline-variant rounded text-primary focus:ring-primary focus:ring-offset-0 focus:ring-offset-background" 
                id="terms" 
                type="checkbox"
                checked={form.terms}
                onChange={(e) => update("terms", e.target.checked)}
                required
              />
            </div>
            <div className="text-sm">
              <label className="font-body-sm text-on-surface-variant" htmlFor="terms">
                I agree to the <a className="text-primary hover:underline" href="#">Terms of Service</a> and <a className="text-primary hover:underline" href="#">Privacy Policy</a>
              </label>
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
            disabled={isLoading || !form.terms || form.password !== form.confirmPassword}
            className="w-full bg-primary-container text-background font-bold text-lg py-sm px-lg rounded-lg hover:scale-[1.02] hover:brightness-110 active:scale-[0.98] transition-all duration-200 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? "Creating..." : "Create Account"}
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

          {/* Sign In Link */}
          <p className="text-center font-body-sm text-on-surface-variant pt-sm">
            Already have an account?{" "}
            <Link href="/login" className="text-primary hover:underline font-semibold transition-colors duration-200">Sign in</Link>
          </p>
        </form>
      </motion.div>
    </div>
  );
}
