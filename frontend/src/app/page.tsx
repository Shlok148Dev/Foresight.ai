"use client";

import React from "react";
import Link from "next/link";
import { Eye, Radar, LineChart, Zap, ArrowRight } from "lucide-react";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-background text-on-surface font-sans selection:bg-primary-container selection:text-on-primary-container">
      {/* Top Navigation */}
      <header className="w-full fixed top-0 left-0 z-50 glass-panel border-b-0 h-16 flex justify-between items-center px-lg">
        <div className="flex items-center gap-sm text-xl font-bold text-primary">
          <Eye className="w-6 h-6" />
          <span>Foresight</span>
        </div>
        <div className="hidden md:flex gap-lg text-on-surface-variant text-sm font-medium">
          <Link href="#features" className="hover:text-primary transition-colors">Features</Link>
          <Link href="#how-it-works" className="hover:text-primary transition-colors">How it Works</Link>
          <Link href="#pricing" className="hover:text-primary transition-colors">Pricing</Link>
        </div>
        <div>
          <Link href="/login" className="text-on-surface-variant text-sm font-medium hover:text-primary mr-md transition-colors">
            Log In
          </Link>
          <Link href="/signup" className="btn-primary px-lg py-sm rounded text-sm font-bold">
            Get Started
          </Link>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative pt-[120px] pb-xxl px-gutter min-h-[921px] flex flex-col justify-center items-center text-center overflow-hidden">
        {/* Abstract Background Element */}
        <div className="absolute inset-0 z-0 opacity-20 pointer-events-none flex justify-center items-center">
          <div className="w-[800px] h-[800px] rounded-full bg-primary-container blur-[150px] mix-blend-screen" />
        </div>
        
        <div className="relative z-10 max-w-container-max mx-auto w-full">
          <h1 className="text-4xl md:text-6xl font-bold text-on-surface mb-md tracking-tight leading-tight">
            See trends before they break out
          </h1>
          <p className="text-lg text-on-surface-variant max-w-[600px] mx-auto mb-xl leading-relaxed">
            Predictive trend intelligence powered by AI. Stay ahead of the curve with real-time analysis of global signals.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-md justify-center items-center mb-xxl">
            <Link href="/signup" className="btn-primary px-xl py-md rounded-lg text-lg font-semibold flex items-center gap-2 w-full sm:w-auto justify-center">
              Start Exploring
              <ArrowRight className="w-5 h-5" />
            </Link>
          </div>
          
          {/* Trend Visualization Graphic */}
          <div className="w-full max-w-[900px] mx-auto h-[300px] md:h-[400px] glass-panel rounded-xl flex items-end p-md relative overflow-hidden">
            <svg className="w-full h-full" preserveAspectRatio="none" viewBox="0 0 1000 300">
              {/* Grid Lines */}
              <path d="M0,50 L1000,50 M0,100 L1000,100 M0,150 L1000,150 M0,200 L1000,200 M0,250 L1000,250" fill="none" opacity="0.5" stroke="#2D3748" strokeWidth="1" />
              {/* Lines */}
              <path className="animated-line" d="M0,280 C200,280 300,150 500,200 C700,250 800,80 1000,40" fill="none" stroke="#0ECDC4" strokeWidth="4" style={{ animationDelay: '0.2s' }} />
              <path className="animated-line" d="M0,290 C250,290 350,220 500,240 C650,260 750,120 1000,90" fill="none" stroke="#454a67" strokeWidth="3" style={{ animationDelay: '0.6s' }} />
              <path className="animated-line" d="M0,270 C150,260 250,180 400,210 C550,240 700,150 1000,120" fill="none" stroke="#859492" strokeDasharray="5,5" strokeWidth="2" style={{ animationDelay: '1s' }} />
              {/* Glow */}
              <path d="M0,280 C200,280 300,150 500,200 C700,250 800,80 1000,40 L1000,300 L0,300 Z" fill="url(#gradient-teal)" opacity="0.1" />
              <defs>
                <linearGradient id="gradient-teal" x1="0%" x2="0%" y1="0%" y2="100%">
                  <stop offset="0%" stopColor="#0ECDC4" stopOpacity="1" />
                  <stop offset="100%" stopColor="#0ECDC4" stopOpacity="0" />
                </linearGradient>
              </defs>
            </svg>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-xxl px-gutter max-w-container-max mx-auto">
        <h2 className="text-3xl md:text-4xl font-bold text-on-surface text-center mb-xl">
          Core Intelligence Capabilities
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-lg">
          <div className="glass-panel p-lg rounded-xl interactive-card flex flex-col gap-md">
            <div className="w-12 h-12 rounded-lg bg-surface-variant flex items-center justify-center text-primary">
              <Radar className="w-8 h-8" />
            </div>
            <h3 className="text-xl font-semibold text-on-surface">Early Detection</h3>
            <p className="text-base text-on-surface-variant flex-grow">
              Scan millions of data points across global networks to identify weak signals before they become mainstream noise.
            </p>
          </div>
          <div className="glass-panel p-lg rounded-xl interactive-card flex flex-col gap-md">
            <div className="w-12 h-12 rounded-lg bg-surface-variant flex items-center justify-center text-primary">
              <LineChart className="w-8 h-8" />
            </div>
            <h3 className="text-xl font-semibold text-on-surface">Accurate Predictions</h3>
            <p className="text-base text-on-surface-variant flex-grow">
              Our proprietary ML models weigh historical context against real-time momentum to forecast trajectory with high precision.
            </p>
          </div>
          <div className="glass-panel p-lg rounded-xl interactive-card flex flex-col gap-md">
            <div className="w-12 h-12 rounded-lg bg-surface-variant flex items-center justify-center text-primary">
              <Zap className="w-8 h-8" />
            </div>
            <h3 className="text-xl font-semibold text-on-surface">Real-Time Insights</h3>
            <p className="text-base text-on-surface-variant flex-grow">
              Access dashboards that update at the speed of the internet, ensuring you never miss critical shifts in your industry.
            </p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="w-full bg-background text-primary text-sm border-t border-outline-variant flex flex-col md:flex-row justify-between items-center py-lg px-xl mt-xxl">
        <div className="text-xs font-bold uppercase tracking-wide text-on-surface-variant mb-md md:mb-0">
          © 2026 Foresight Predictive Intelligence
        </div>
        <div className="flex flex-wrap gap-md justify-center">
          <Link href="#" className="text-on-surface-variant hover:text-primary transition-colors">About</Link>
          <Link href="#" className="text-on-surface-variant hover:text-primary transition-colors">Pricing</Link>
          <Link href="#" className="text-on-surface-variant hover:text-primary transition-colors">Docs</Link>
          <Link href="https://github.com/Shlok148Dev/Foresight.ai" className="text-on-surface-variant hover:text-primary transition-colors">GitHub</Link>
          <Link href="#" className="text-on-surface-variant hover:text-primary transition-colors">Twitter</Link>
          <Link href="#" className="text-on-surface-variant hover:text-primary transition-colors">Email</Link>
        </div>
      </footer>
    </div>
  );
}
