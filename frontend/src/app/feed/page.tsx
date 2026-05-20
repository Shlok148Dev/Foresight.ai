"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import {
  Zap, RefreshCw, BarChart2, MessageSquare, Clock, Globe, Settings2, ShieldAlert
} from "lucide-react";
import { Sidebar } from "@/components";
import { useAuth } from "@/hooks/useAuth";
import { useDetections, useRunPipeline } from "@/hooks/useSignals";
import { staggerContainer, staggerItem } from "@/lib/animations";

export default function FeedPage() {
  const router = useRouter();
  const { user, loadUser, token } = useAuth();

  /* State filters */
  const [stage, setStage] = useState<string>("");
  const [minConfidence, setMinConfidence] = useState<number>(0);
  const [sortBy, setSortBy] = useState<string>("confidence");
  const [selectedDetection, setSelectedDetection] = useState<any | null>(null);

  /* React query hooks */
  const {
    data: detectionsData,
    isLoading,
    refetch,
    isRefetching,
  } = useDetections({
    stage: stage || undefined,
    min_confidence: minConfidence > 0 ? minConfidence : undefined,
    sort_by: sortBy,
    limit: 100,
  });

  const { mutate: runPipeline, isPending: isRunningPipeline } = useRunPipeline();

  /* Load user and auth guard */
  useEffect(() => {
    if (!token) {
      router.push("/login");
      return;
    }
    if (!user) loadUser();
  }, [token, user, loadUser, router]);

  const handleRunPipeline = () => {
    runPipeline(24, {
      onSuccess: (data) => {
        alert(
          `Pipeline execution complete!\nStatus: ${data.status}\nCreated Detections: ${data.detections_created}\nSignals Processed: ${data.signals_processed}`
        );
      },
    });
  };

  const detections = detectionsData?.detections || [];

  return (
    <div className="bg-background text-on-surface antialiased min-h-screen flex flex-col md:flex-row font-body-md selection:bg-primary-container selection:text-on-primary-container">
      <Sidebar />

      {/* TopAppBar */}
      <header className="fixed top-0 right-0 w-[calc(100%-240px)] z-30 bg-surface/80 backdrop-blur-xl border-b border-outline-variant flex justify-between items-center h-16 px-lg transition-all duration-200 hidden md:flex">
        <div className="flex-1 max-w-md relative">
          <div className="flex items-center gap-2">
            <Zap className="h-5 w-5 text-primary" />
            <h1 className="text-xl font-bold text-on-surface">Trend Feed</h1>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => refetch()}
            disabled={isLoading || isRefetching}
            className="flex items-center gap-2 px-4 py-2 border border-outline-variant rounded-lg text-on-surface font-semibold hover:bg-surface-variant transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`h-4 w-4 ${isRefetching ? "animate-spin" : ""}`} />
            Refresh
          </button>
          <button
            onClick={handleRunPipeline}
            disabled={isRunningPipeline}
            className="flex items-center gap-2 px-4 py-2 bg-primary-container text-background font-bold rounded-lg hover:brightness-110 active:scale-[0.98] transition-all disabled:opacity-50"
          >
            <Zap className={`h-4 w-4 ${isRunningPipeline ? "animate-pulse" : ""}`} />
            {isRunningPipeline ? "Running NLP Pipeline..." : "Trigger Pipeline"}
          </button>
        </div>
      </header>

      {/* Mobile TopAppBar */}
      <header className="md:hidden flex justify-between items-center px-md py-sm border-b border-outline-variant bg-surface/80 backdrop-blur-xl sticky top-0 z-40">
        <div className="flex items-center gap-2">
          <Zap className="h-5 w-5 text-primary" />
          <h1 className="text-lg font-bold text-on-surface">Trend Feed</h1>
        </div>
        <button
            onClick={handleRunPipeline}
            disabled={isRunningPipeline}
            className="flex items-center p-2 bg-primary-container text-background rounded-lg hover:brightness-110 active:scale-[0.98] transition-all disabled:opacity-50"
          >
            <Zap className={`h-4 w-4 ${isRunningPipeline ? "animate-pulse" : ""}`} />
          </button>
      </header>

      {/* Main Content */}
      <main className="flex-1 md:ml-[240px] pt-8 md:pt-[88px] px-md md:px-xl pb-xl min-h-screen max-w-container-max mx-auto w-full relative">
        
        {/* Filters Bar */}
        <div className="bg-surface border border-outline-variant rounded-xl p-md mb-lg flex flex-wrap items-center gap-6">
          {/* Stage Filter */}
          <div className="flex flex-col gap-1">
            <label className="text-xs font-bold text-on-surface-variant uppercase tracking-wider flex items-center gap-1">
              <Settings2 className="w-3 h-3" /> Spread Stage
            </label>
            <select
              value={stage}
              onChange={(e) => setStage(e.target.value)}
              className="bg-background border border-outline-variant text-sm text-on-surface rounded-lg px-3 py-2 outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all cursor-pointer"
            >
              <option value="">All Stages</option>
              <option value="embryonic">Embryonic</option>
              <option value="emerging">Emerging</option>
              <option value="accelerating">Accelerating</option>
              <option value="peaking">Peaking</option>
              <option value="declining">Declining</option>
            </select>
          </div>

          {/* Min Confidence */}
          <div className="flex flex-col gap-1 flex-1 min-w-[200px]">
            <div className="flex justify-between items-center">
              <label className="text-xs font-bold text-on-surface-variant uppercase tracking-wider flex items-center gap-1">
                <ShieldAlert className="w-3 h-3" /> Min Confidence
              </label>
              <span className="text-xs font-bold text-primary">
                {Math.round(minConfidence * 100)}%
              </span>
            </div>
            <input
              type="range"
              min="0"
              max="1.0"
              step="0.05"
              value={minConfidence}
              onChange={(e) => setMinConfidence(parseFloat(e.target.value))}
              className="w-full h-1 bg-surface-variant rounded-lg appearance-none cursor-pointer accent-primary"
            />
          </div>

          {/* Sort By */}
          <div className="flex flex-col gap-1">
            <label className="text-xs font-bold text-on-surface-variant uppercase tracking-wider flex items-center gap-1">
              <BarChart2 className="w-3 h-3" /> Sort By
            </label>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="bg-background border border-outline-variant text-sm text-on-surface rounded-lg px-3 py-2 outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all cursor-pointer"
            >
              <option value="confidence">Confidence Score</option>
              <option value="velocity">Velocity (signals/hr)</option>
              <option value="signal_count">Signal Volume</option>
              <option value="first_seen">First Detected</option>
            </select>
          </div>
        </div>

        {/* Feed List */}
        {isLoading ? (
          <div className="flex flex-col items-center justify-center py-20 gap-4">
            <div className="w-10 h-10 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
            <p className="text-on-surface-variant text-sm font-semibold animate-pulse">
              Analyzing recent signals...
            </p>
          </div>
        ) : detections.length > 0 ? (
          <motion.div
            variants={staggerContainer}
            initial="hidden"
            animate="visible"
            className="grid gap-4 md:grid-cols-2 lg:grid-cols-3"
          >
            {detections.map((d: any) => (
              <motion.div
                key={d.id}
                variants={staggerItem}
                onClick={() => setSelectedDetection(d)}
                className="cursor-pointer h-full"
              >
                <div className="bg-surface border border-outline-variant hover:border-primary rounded-xl p-5 flex flex-col justify-between h-full transition-all hover:scale-[1.01] hover:shadow-[0_0_20px_rgba(73,233,224,0.1)] group">
                  <div className="space-y-4">
                    <div className="flex items-start justify-between gap-3">
                      <h3 className="font-bold text-on-surface text-lg group-hover:text-primary transition-colors line-clamp-2">
                        {d.topic}
                      </h3>
                      <span className="bg-surface-variant text-on-surface-variant text-xs font-bold uppercase tracking-wider px-2 py-1 rounded">
                        {d.stage}
                      </span>
                    </div>

                    <p className="text-sm text-on-surface-variant line-clamp-3 leading-relaxed">
                      {d.description || "Detailed summary context is still being processed by the analytical engine."}
                    </p>

                    <div className="flex flex-wrap gap-1">
                      {d.keywords?.slice(0, 4).map((kw: string) => (
                        <span key={kw} className="bg-background border border-outline-variant text-on-surface-variant text-xs px-2 py-0.5 rounded">
                          #{kw}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div className="border-t border-outline-variant mt-6 pt-4 flex items-center justify-between">
                    <div className="flex gap-4">
                      <div className="text-left">
                        <p className="text-[10px] uppercase font-bold text-on-surface-variant tracking-wider">
                          Velocity
                        </p>
                        <p className="text-sm font-bold text-on-surface">
                          {d.velocity?.toFixed(1)}/h
                        </p>
                      </div>
                      <div className="text-left">
                        <p className="text-[10px] uppercase font-bold text-on-surface-variant tracking-wider">
                          Volume
                        </p>
                        <p className="text-sm font-bold text-on-surface">
                          {d.signal_count}
                        </p>
                      </div>
                    </div>

                    <div className="text-right">
                      <p className="text-[10px] uppercase font-bold text-on-surface-variant tracking-wider">
                        Confidence
                      </p>
                      <p className="text-xl font-black text-primary">
                        {Math.round(d.confidence * 100)}%
                      </p>
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}
          </motion.div>
        ) : (
          <div className="bg-surface border border-outline-variant rounded-xl p-10 text-center flex flex-col items-center justify-center max-w-xl mx-auto mt-10">
            <Zap className="h-12 w-12 text-on-surface-variant mb-4 opacity-50" />
            <h3 className="text-lg font-bold text-on-surface mb-2">
              No trends detected matching filters
            </h3>
            <p className="text-sm text-on-surface-variant max-w-sm mb-6">
              Try widening your filters or execute the NLP detection pipeline to cluster recent signals.
            </p>
            <button
              onClick={handleRunPipeline}
              disabled={isRunningPipeline}
              className="px-6 py-2 bg-primary-container text-background font-bold rounded-lg hover:brightness-110 active:scale-[0.98] transition-all disabled:opacity-50"
            >
              {isRunningPipeline ? "Running..." : "Trigger Pipeline"}
            </button>
          </div>
        )}
      </main>

      {/* Detail Modal Overlay */}
      <AnimatePresence>
        {selectedDetection && (
          <div className="fixed inset-0 z-50 flex items-center justify-center px-4 py-8">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setSelectedDetection(null)}
              className="absolute inset-0 bg-background/80 backdrop-blur-sm"
            ></motion.div>
            
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              className="relative w-full max-w-2xl bg-surface border border-outline-variant rounded-2xl shadow-2xl overflow-hidden max-h-full flex flex-col"
            >
              <div className="p-6 overflow-y-auto">
                <div className="flex items-center justify-between mb-4">
                  <span className="bg-primary/20 text-primary px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider">
                    {selectedDetection.stage}
                  </span>
                  <div className="flex items-center gap-1 text-xs text-on-surface-variant font-semibold">
                    <Clock className="w-4 h-4" /> 
                    {new Date(selectedDetection.first_seen).toLocaleDateString()}
                  </div>
                </div>
                
                <h2 className="text-3xl font-bold text-on-surface leading-tight mb-6">
                  {selectedDetection.topic}
                </h2>

                {/* Metrics */}
                <div className="grid grid-cols-3 gap-4 border-y border-outline-variant py-4 mb-6 bg-background/50 rounded-lg px-2">
                  <div className="text-center">
                    <p className="text-xs text-on-surface-variant uppercase font-bold tracking-wider mb-1">
                      Confidence
                    </p>
                    <p className="text-3xl font-black text-primary">
                      {Math.round(selectedDetection.confidence * 100)}%
                    </p>
                  </div>
                  <div className="text-center border-x border-outline-variant">
                    <p className="text-xs text-on-surface-variant uppercase font-bold tracking-wider mb-1">
                      Velocity
                    </p>
                    <p className="text-3xl font-black text-tertiary-container">
                      {selectedDetection.velocity?.toFixed(1)}/h
                    </p>
                  </div>
                  <div className="text-center">
                    <p className="text-xs text-on-surface-variant uppercase font-bold tracking-wider mb-1">
                      Signal Volume
                    </p>
                    <p className="text-3xl font-black text-on-surface">
                      {selectedDetection.signal_count}
                    </p>
                  </div>
                </div>

                {/* Description */}
                <div className="space-y-2 mb-6">
                  <h4 className="text-sm font-bold text-on-surface flex items-center gap-2">
                    <BarChart2 className="h-4 w-4 text-primary" /> Trend Summary
                  </h4>
                  <p className="text-sm text-on-surface-variant leading-relaxed bg-background/80 rounded-xl p-4 border border-outline-variant">
                    {selectedDetection.description || "No full description compiled. Trigger background clustering to update details."}
                  </p>
                </div>

                {/* Action Prompt */}
                {selectedDetection.action_prompt && (
                  <div className="space-y-2 mb-6">
                    <h4 className="text-sm font-bold text-primary flex items-center gap-2">
                      <MessageSquare className="h-4 w-4" /> AI Action Prompt
                    </h4>
                    <p className="text-sm text-primary leading-relaxed bg-primary/10 rounded-xl p-4 border border-primary/20 font-mono">
                      {selectedDetection.action_prompt}
                    </p>
                  </div>
                )}

                {/* Keywords and Platforms */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <h4 className="text-xs font-bold text-on-surface-variant uppercase tracking-wider flex items-center gap-1">
                      <Globe className="h-3 w-3" /> Sources
                    </h4>
                    <div className="flex flex-wrap gap-1.5">
                      {selectedDetection.platforms?.map((p: string) => (
                        <span key={p} className="bg-surface-variant text-on-surface-variant text-xs px-2 py-1 rounded">
                          {p}
                        </span>
                      ))}
                    </div>
                  </div>
                  <div className="space-y-2">
                    <h4 className="text-xs font-bold text-on-surface-variant uppercase tracking-wider flex items-center gap-1">
                      <Zap className="h-3 w-3" /> Keywords
                    </h4>
                    <div className="flex flex-wrap gap-1.5">
                      {selectedDetection.keywords?.map((kw: string) => (
                        <span key={kw} className="bg-background border border-outline-variant text-on-surface-variant text-xs px-2 py-1 rounded">
                          #{kw}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              <div className="p-4 border-t border-outline-variant bg-background flex justify-end">
                <button
                  onClick={() => setSelectedDetection(null)}
                  className="px-6 py-2 bg-surface-variant hover:bg-surface-bright text-on-surface font-semibold rounded-lg transition-colors"
                >
                  Close
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}
