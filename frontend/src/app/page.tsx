"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import {
  TrendingUp,
  Zap,
  Eye,
  BarChart3,
  Globe,
  Shield,
  ChevronRight,
  Sparkles,
  Play,
  ArrowRight,
} from "lucide-react";

/* ── Animated Counter ──────────────────────────────────────────── */

function AnimatedNumber({ target, suffix = "" }: { target: number; suffix?: string }) {
  const [count, setCount] = useState(0);
  useEffect(() => {
    const duration = 2000;
    const steps = 60;
    const increment = target / steps;
    let current = 0;
    const timer = setInterval(() => {
      current += increment;
      if (current >= target) {
        setCount(target);
        clearInterval(timer);
      } else {
        setCount(Math.floor(current));
      }
    }, duration / steps);
    return () => clearInterval(timer);
  }, [target]);
  return (
    <span className="tabular-nums">
      {count.toLocaleString()}{suffix}
    </span>
  );
}

/* ── Feature Card ──────────────────────────────────────────────── */

function FeatureCard({
  icon: Icon,
  title,
  description,
  gradient,
}: {
  icon: React.ElementType;
  title: string;
  description: string;
  gradient: string;
}) {
  return (
    <div className="group relative rounded-2xl border border-[#2A3050] bg-[#0F1419] p-8 transition-all duration-300 hover:border-[#00D4AA] hover:shadow-[0_0_30px_rgba(0,212,170,0.08)]">
      <div
        className={`mb-5 inline-flex h-12 w-12 items-center justify-center rounded-xl ${gradient}`}
      >
        <Icon className="h-6 w-6 text-white" />
      </div>
      <h3 className="mb-3 text-xl font-semibold text-white">{title}</h3>
      <p className="leading-relaxed text-[#A0AEC0]">{description}</p>
    </div>
  );
}

/* ── Stat Card ─────────────────────────────────────────────────── */

function StatCard({ value, label }: { value: React.ReactNode; label: string }) {
  return (
    <div className="text-center">
      <div className="mb-1 text-4xl font-bold gradient-text">{value}</div>
      <div className="text-sm text-[#718096]">{label}</div>
    </div>
  );
}

/* ── Signal Pill (floating demo element) ───────────────────────── */

function SignalPill({
  label,
  stage,
  delay,
}: {
  label: string;
  stage: "embryonic" | "emerging" | "accelerating";
  delay: number;
}) {
  const colors = {
    embryonic: "border-[#6C63FF] text-[#6C63FF]",
    emerging: "border-[#00D4AA] text-[#00D4AA]",
    accelerating: "border-[#F59E0B] text-[#F59E0B]",
  };
  return (
    <div
      className={`inline-flex items-center gap-2 rounded-full border bg-[#0F1419]/80 px-4 py-2 text-sm backdrop-blur-sm ${colors[stage]}`}
      style={{ animation: `float 4s ease-in-out ${delay}s infinite` }}
    >
      <span className="relative flex h-2 w-2">
        <span
          className={`absolute inline-flex h-full w-full animate-ping rounded-full opacity-75 ${
            stage === "embryonic"
              ? "bg-[#6C63FF]"
              : stage === "emerging"
              ? "bg-[#00D4AA]"
              : "bg-[#F59E0B]"
          }`}
        />
        <span
          className={`relative inline-flex h-2 w-2 rounded-full ${
            stage === "embryonic"
              ? "bg-[#6C63FF]"
              : stage === "emerging"
              ? "bg-[#00D4AA]"
              : "bg-[#F59E0B]"
          }`}
        />
      </span>
      {label}
    </div>
  );
}

/* ══════════════════════════════════════════════════════════════════
   LANDING PAGE
   ══════════════════════════════════════════════════════════════════ */

export default function Home() {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    setIsVisible(true);
  }, []);

  return (
    <div className="relative min-h-screen overflow-hidden">
      {/* ── Ambient background ────────────────────────────────── */}
      <div className="animated-gradient fixed inset-0 -z-10" />
      <div className="pointer-events-none fixed inset-0 -z-10 bg-[radial-gradient(ellipse_at_top,rgba(108,99,255,0.12),transparent_60%)]" />

      {/* ── Navbar ────────────────────────────────────────────── */}
      <nav className="glass fixed left-0 right-0 top-0 z-50 border-b border-white/5">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-6">
          <Link href="/" className="flex items-center gap-2">
            <Eye className="h-7 w-7 text-[#00D4AA]" />
            <span className="text-xl font-bold tracking-tight">
              Fore<span className="text-[#00D4AA]">sight</span>
            </span>
          </Link>

          <div className="hidden items-center gap-8 md:flex">
            <Link href="#features" className="text-sm text-[#A0AEC0] transition-colors hover:text-white">
              Features
            </Link>
            <Link href="#how-it-works" className="text-sm text-[#A0AEC0] transition-colors hover:text-white">
              How It Works
            </Link>
            <Link href="#pricing" className="text-sm text-[#A0AEC0] transition-colors hover:text-white">
              Pricing
            </Link>
          </div>

          <div className="flex items-center gap-3">
            <Link
              href="/login"
              className="rounded-xl px-5 py-2 text-sm font-medium text-[#A0AEC0] transition-colors hover:text-white"
            >
              Log In
            </Link>
            <Link
              href="/register"
              className="gradient-bg rounded-xl px-5 py-2.5 text-sm font-semibold text-white shadow-lg shadow-[#6C63FF]/20 transition-all hover:shadow-[#6C63FF]/40 hover:brightness-110"
            >
              Get Started Free
            </Link>
          </div>
        </div>
      </nav>

      {/* ── Hero Section ──────────────────────────────────────── */}
      <section className="relative flex min-h-screen flex-col items-center justify-center px-6 pt-16">
        {/* Floating signal pills */}
        <div className="pointer-events-none absolute inset-0 overflow-hidden">
          <div className="absolute left-[8%] top-[22%] hidden lg:block">
            <SignalPill label="AI Agents" stage="emerging" delay={0} />
          </div>
          <div className="absolute right-[10%] top-[28%] hidden lg:block">
            <SignalPill label="Quantum ML" stage="embryonic" delay={1} />
          </div>
          <div className="absolute left-[15%] bottom-[30%] hidden lg:block">
            <SignalPill label="Spatial Web" stage="accelerating" delay={2} />
          </div>
          <div className="absolute right-[12%] bottom-[25%] hidden lg:block">
            <SignalPill label="Edge AI" stage="emerging" delay={0.5} />
          </div>
        </div>

        <div
          className={`mx-auto max-w-4xl text-center transition-all duration-1000 ${
            isVisible ? "translate-y-0 opacity-100" : "translate-y-8 opacity-0"
          }`}
        >
          {/* Badge */}
          <div className="mb-8 inline-flex items-center gap-2 rounded-full border border-[#6C63FF]/30 bg-[#6C63FF]/10 px-4 py-1.5 text-sm text-[#6C63FF]">
            <Sparkles className="h-4 w-4" />
            Powered by MiroFish Multi-Agent Simulation
          </div>

          {/* Headline */}
          <h1 className="mb-6 text-5xl font-bold leading-tight tracking-tight md:text-7xl">
            See Trends{" "}
            <span className="gradient-text">Before</span>
            <br />
            They Break Out
          </h1>

          {/* Subheading */}
          <p className="mx-auto mb-10 max-w-2xl text-lg leading-relaxed text-[#A0AEC0] md:text-xl">
            Foresight detects emerging signals across{" "}
            <span className="text-white font-medium">50+ platforms</span> and predicts trend
            trajectories using AI-powered behavioral simulation — days before
            Google Trends.
          </p>

          {/* CTAs */}
          <div className="flex flex-col items-center gap-4 sm:flex-row sm:justify-center">
            <Link
              href="/register"
              className="gradient-bg group flex items-center gap-2 rounded-2xl px-8 py-4 text-lg font-semibold text-white shadow-xl shadow-[#6C63FF]/25 transition-all hover:shadow-[#6C63FF]/40 hover:brightness-110"
            >
              Start Detecting Free
              <ArrowRight className="h-5 w-5 transition-transform group-hover:translate-x-1" />
            </Link>
            <button className="flex items-center gap-2 rounded-2xl border border-[#2A3050] bg-[#0F1419] px-8 py-4 text-lg font-medium text-[#A0AEC0] transition-all hover:border-[#00D4AA] hover:text-white">
              <Play className="h-5 w-5 text-[#00D4AA]" />
              Watch Demo
            </button>
          </div>
        </div>

        {/* Stats bar */}
        <div
          className={`mt-20 grid grid-cols-2 gap-8 md:grid-cols-4 transition-all duration-1000 delay-500 ${
            isVisible ? "translate-y-0 opacity-100" : "translate-y-8 opacity-0"
          }`}
        >
          <StatCard
            value={<AnimatedNumber target={50} suffix="+" />}
            label="Signal Sources"
          />
          <StatCard
            value={<AnimatedNumber target={1000000} suffix="" />}
            label="Agent Simulations / Day"
          />
          <StatCard
            value={<><AnimatedNumber target={48} />–<AnimatedNumber target={72} />h</>}
            label="Early Detection"
          />
          <StatCard
            value={<><AnimatedNumber target={85} />%</>}
            label="Prediction Accuracy"
          />
        </div>

        {/* Scroll indicator */}
        <div className="absolute bottom-8 left-1/2 -translate-x-1/2 animate-bounce">
          <ChevronRight className="h-6 w-6 rotate-90 text-[#718096]" />
        </div>
      </section>

      {/* ── Features Grid ─────────────────────────────────────── */}
      <section id="features" className="relative px-6 py-32">
        <div className="mx-auto max-w-7xl">
          <div className="mb-16 text-center">
            <h2 className="mb-4 text-4xl font-bold md:text-5xl">
              Intelligence That{" "}
              <span className="gradient-text">Moves Markets</span>
            </h2>
            <p className="mx-auto max-w-2xl text-lg text-[#A0AEC0]">
              Every feature is designed to give you an unfair advantage in
              detecting and acting on emerging trends.
            </p>
          </div>

          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            <FeatureCard
              icon={TrendingUp}
              title="Predictive Signal Detection"
              description="Detect emerging signals 48-72 hours before Google Trends. Multi-source NLP pipeline processes data from TikTok, Discord, Reddit, Telegram, and 46+ more platforms."
              gradient="bg-gradient-to-br from-[#6C63FF] to-[#8B7FFF]"
            />
            <FeatureCard
              icon={Globe}
              title="Multi-Agent Simulation"
              description="MiroFish-powered behavioral simulation with 1M+ agents predicts exactly how trends will spread — which communities amplify, mutation paths, and mainstream ETA."
              gradient="bg-gradient-to-br from-[#00D4AA] to-[#00E6B8]"
            />
            <FeatureCard
              icon={BarChart3}
              title="Simulation Replay"
              description="Watch exactly how a trend spread through communities with interactive force-directed graph visualization. Scrub the timeline, inspect nodes, and export insights."
              gradient="bg-gradient-to-br from-[#F59E0B] to-[#FBBF24]"
            />
            <FeatureCard
              icon={Zap}
              title="Real-Time Feed"
              description="Personalized signal stream ranked by your interest model. WebSocket-powered live updates ensure you never miss a breakout moment."
              gradient="bg-gradient-to-br from-[#FF6B9D] to-[#FF8FAB]"
            />
            <FeatureCard
              icon={Shield}
              title="Accuracy Tracking"
              description="Every prediction is validated against reality. Track your signal accuracy over time with transparent metrics — we publish our hit rate."
              gradient="bg-gradient-to-br from-[#3B82F6] to-[#60A5FA]"
            />
            <FeatureCard
              icon={Sparkles}
              title="Action Prompts"
              description="Every signal comes with 'the one thing to do right now.' No analysis paralysis — just clear, actionable intelligence tailored to your role."
              gradient="bg-gradient-to-br from-[#8B5CF6] to-[#A78BFA]"
            />
          </div>
        </div>
      </section>

      {/* ── How It Works ──────────────────────────────────────── */}
      <section id="how-it-works" className="relative px-6 py-32">
        <div className="mx-auto max-w-5xl">
          <div className="mb-16 text-center">
            <h2 className="mb-4 text-4xl font-bold md:text-5xl">
              How <span className="gradient-text">Foresight</span> Works
            </h2>
          </div>

          <div className="grid gap-12 md:grid-cols-3">
            {[
              {
                step: "01",
                title: "Signal Detection",
                desc: "Our NLP pipeline continuously monitors 50+ platforms, extracting emerging patterns using clustering and semantic analysis.",
                color: "#6C63FF",
              },
              {
                step: "02",
                title: "Agent Simulation",
                desc: "MiroFish simulates how 1M+ behavioral agents would react — predicting spread path, virality coefficient, and mainstream ETA.",
                color: "#00D4AA",
              },
              {
                step: "03",
                title: "Actionable Insight",
                desc: "You receive a prioritized feed with confidence scores, spread predictions, and exactly what to do right now. Act fast.",
                color: "#F59E0B",
              },
            ].map((item) => (
              <div key={item.step} className="text-center">
                <div
                  className="mx-auto mb-6 flex h-16 w-16 items-center justify-center rounded-2xl text-2xl font-bold"
                  style={{
                    background: `${item.color}15`,
                    color: item.color,
                    border: `1px solid ${item.color}30`,
                  }}
                >
                  {item.step}
                </div>
                <h3 className="mb-3 text-xl font-semibold">{item.title}</h3>
                <p className="text-[#A0AEC0]">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── CTA Section ───────────────────────────────────────── */}
      <section className="relative px-6 py-32">
        <div className="mx-auto max-w-3xl rounded-3xl border border-[#2A3050] bg-[#0F1419] p-12 text-center md:p-16">
          <h2 className="mb-4 text-3xl font-bold md:text-4xl">
            Ready to See the Future?
          </h2>
          <p className="mb-8 text-lg text-[#A0AEC0]">
            Join thousands of analysts, creators, and founders who detect
            trends before they break out.
          </p>
          <Link
            href="/register"
            className="gradient-bg inline-flex items-center gap-2 rounded-2xl px-10 py-4 text-lg font-semibold text-white shadow-xl shadow-[#6C63FF]/25 transition-all hover:shadow-[#6C63FF]/40 hover:brightness-110"
          >
            Get Started Free
            <ArrowRight className="h-5 w-5" />
          </Link>
          <p className="mt-4 text-sm text-[#718096]">
            No credit card required · 5 signals/day free forever
          </p>
        </div>
      </section>

      {/* ── Footer ────────────────────────────────────────────── */}
      <footer className="border-t border-[#2A3050] px-6 py-12">
        <div className="mx-auto flex max-w-7xl flex-col items-center justify-between gap-6 md:flex-row">
          <div className="flex items-center gap-2">
            <Eye className="h-5 w-5 text-[#00D4AA]" />
            <span className="font-semibold">Foresight</span>
          </div>
          <div className="flex gap-8 text-sm text-[#718096]">
            <Link href="#" className="hover:text-white">About</Link>
            <Link href="#" className="hover:text-white">API Docs</Link>
            <Link href="#" className="hover:text-white">GitHub</Link>
            <Link href="#" className="hover:text-white">Privacy</Link>
          </div>
          <div className="text-sm text-[#718096]">
            © 2026 Foresight. Open source.
          </div>
        </div>
      </footer>
    </div>
  );
}
