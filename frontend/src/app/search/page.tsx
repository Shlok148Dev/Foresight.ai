"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { Search as SearchIcon, TrendingUp, Radio, ExternalLink, Activity, Users, ArrowRight } from "lucide-react";
import { Sidebar } from "@/components";
import { useAuth } from "@/hooks/useAuth";
import { useSearch } from "@/hooks/useSignals";
import { staggerContainer, staggerItem } from "@/lib/animations";

export default function SearchPage() {
  const router = useRouter();
  const { user, loadUser, token } = useAuth();

  const [query, setQuery] = useState("");
  const [debouncedQuery, setDebouncedQuery] = useState("");
  const [activeTab, setActiveTab] = useState<"detections" | "signals">("detections");
  const [selectedDetection, setSelectedDetection] = useState<any | null>(null);

  /* Debounce search input */
  useEffect(() => {
    const handler = setTimeout(() => setDebouncedQuery(query), 300);
    return () => clearTimeout(handler);
  }, [query]);

  /* Fetch results */
  const { data, isLoading } = useSearch(debouncedQuery);

  /* Auth guard */
  useEffect(() => {
    if (!token) {
      router.push("/login");
      return;
    }
    if (!user) loadUser();
  }, [token, user, loadUser, router]);

  const detections = data?.detections || [];
  const signals = data?.signals || [];

  return (
    <div className="bg-background text-on-surface antialiased min-h-screen flex flex-col md:flex-row font-body-md selection:bg-primary-container selection:text-on-primary-container">
      <Sidebar />

      {/* TopAppBar (Mobile & Desktop) */}
      <header className="fixed top-0 left-0 md:left-[240px] right-0 h-16 z-30 glass-panel border-b border-outline-variant px-lg flex justify-between items-center transition-all duration-200">
        <div className="flex items-center md:hidden">
          <h1 className="font-headline-sm text-headline-sm font-bold text-primary">Foresight</h1>
        </div>
        <div className="hidden md:flex flex-1 max-w-xl mx-auto">
           {/* Header space */}
        </div>
      </header>

      {/* Main Content Canvas */}
      <main className="flex-1 md:ml-[240px] pt-24 px-md md:px-xl pb-xxl flex flex-col gap-lg max-w-container-max mx-auto w-full">
        
        {/* Search Section */}
        <section className="w-full flex flex-col md:flex-row gap-md items-center mb-md">
          <div className="relative w-full">
            <SearchIcon className="absolute left-md top-1/2 transform -translate-y-1/2 text-on-surface-variant w-5 h-5" />
            <input 
              type="text"
              value={query}
              onChange={(e) => {
                setQuery(e.target.value);
                if (selectedDetection) setSelectedDetection(null); // Clear selection on new search
              }}
              className="w-full bg-surface border border-outline-variant text-on-surface rounded-lg pl-xl pr-md py-lg font-body-lg text-lg focus:border-primary focus:ring-1 focus:ring-primary focus:outline-none transition-all placeholder:text-on-surface-variant"
              placeholder="Search trend topics, descriptions, keywords or raw signals..."
            />
          </div>
          <button className="btn-primary font-body-md px-xl py-lg w-full md:w-auto whitespace-nowrap font-semibold rounded-lg h-[60px]">
            Analyze
          </button>
        </section>

        <AnimatePresence mode="wait">
          {selectedDetection ? (
            /* --- DETAIL BENTO GRID (Stitch Design) --- */
            <motion.div 
              key="detail-view"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="space-y-lg w-full"
            >
              <button 
                onClick={() => setSelectedDetection(null)}
                className="flex items-center gap-2 text-on-surface-variant hover:text-primary transition-colors text-sm font-semibold mb-4"
              >
                ← Back to Results
              </button>

              <div className="flex flex-col md:flex-row justify-between items-start md:items-end mb-sm gap-sm">
                <div>
                  <h2 className="font-headline-xl text-3xl font-bold text-on-surface">{selectedDetection.topic}</h2>
                  <div className="flex flex-wrap gap-2 mt-3">
                    <span className="bg-surface-variant text-on-surface px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wider">
                      {selectedDetection.stage}
                    </span>
                    {selectedDetection.keywords?.slice(0, 3).map((kw: string) => (
                      <span key={kw} className="bg-surface-variant text-on-surface-variant px-3 py-1 rounded-full text-xs">
                        #{kw}
                      </span>
                    ))}
                    <span className="bg-primary/10 text-primary px-3 py-1 rounded-full text-xs font-semibold flex items-center gap-1 border border-primary/30">
                      <TrendingUp className="w-4 h-4" /> {(selectedDetection.velocity || 0).toFixed(1)}/h
                    </span>
                  </div>
                </div>
                <div className="text-left md:text-right">
                  <p className="font-headline-sm text-2xl font-bold text-primary">{selectedDetection.signal_count} mentions</p>
                  <p className="text-sm text-on-surface-variant">Analyzed Volume</p>
                </div>
              </div>

              {/* Bento Grid Layout */}
              <div className="grid grid-cols-1 md:grid-cols-12 gap-lg">
                {/* 24-hour velocity chart mock */}
                <div className="bg-surface border border-outline-variant rounded-xl p-lg col-span-1 md:col-span-8 flex flex-col min-h-[300px] interactive-card">
                  <div className="flex justify-between items-center mb-md">
                    <h3 className="font-headline-sm text-lg font-semibold text-on-surface">24-Hour Velocity</h3>
                    <Activity className="w-5 h-5 text-on-surface-variant" />
                  </div>
                  <div className="flex-1 relative w-full h-full border-b border-l border-outline-variant opacity-80 flex items-end overflow-hidden">
                    <svg className="absolute bottom-0 left-0 w-full h-full" preserveAspectRatio="none" viewBox="0 0 100 100">
                      <line x1="0" y1="25" x2="100" y2="25" stroke="#3b4948" strokeWidth="0.5" strokeOpacity="0.5" />
                      <line x1="0" y1="50" x2="100" y2="50" stroke="#3b4948" strokeWidth="0.5" strokeOpacity="0.5" />
                      <line x1="0" y1="75" x2="100" y2="75" stroke="#3b4948" strokeWidth="0.5" strokeOpacity="0.5" />
                      <path d="M0,80 Q10,75 20,60 T40,50 T60,20 T80,30 T100,5" fill="none" stroke="url(#tealGradient)" strokeWidth="2" />
                      <path d="M0,80 Q10,75 20,60 T40,50 T60,20 T80,30 T100,5" fill="none" stroke="#0ecdc4" strokeWidth="1" filter="drop-shadow(0 0 4px #0ecdc4)" />
                      <defs>
                        <linearGradient id="tealGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                          <stop offset="0%" stopColor="#0ecdc4" stopOpacity="0.2" />
                          <stop offset="100%" stopColor="#0ecdc4" stopOpacity="1" />
                        </linearGradient>
                      </defs>
                    </svg>
                  </div>
                </div>

                {/* Info Breakdown */}
                <div className="bg-surface border border-outline-variant rounded-xl p-lg col-span-1 md:col-span-4 flex flex-col interactive-card">
                  <h3 className="font-headline-sm text-lg font-semibold text-on-surface mb-lg">Trend Insight</h3>
                  <div className="flex-1 flex flex-col gap-4">
                    <p className="text-on-surface-variant text-sm leading-relaxed">
                      {selectedDetection.description || "Detailed summary context is still being processed by the analytical engine."}
                    </p>
                    <div className="mt-auto pt-4 border-t border-outline-variant">
                      <div className="flex justify-between items-center text-sm">
                        <span className="text-on-surface-variant">Confidence Score</span>
                        <span className="text-primary font-bold">{Math.round(selectedDetection.confidence * 100)}%</span>
                      </div>
                      <div className="flex justify-between items-center text-sm mt-2">
                        <span className="text-on-surface-variant">First Detected</span>
                        <span className="text-on-surface">{new Date(selectedDetection.first_seen).toLocaleDateString()}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          ) : (
            /* --- SEARCH RESULTS LIST --- */
            <motion.div 
              key="search-list"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="space-y-6"
            >
              {debouncedQuery.trim().length >= 2 ? (
                <>
                  {/* Tab headers */}
                  <div className="flex border-b border-outline-variant gap-6">
                    <button
                      onClick={() => setActiveTab("detections")}
                      className={`pb-3 text-sm font-bold transition-all relative ${
                        activeTab === "detections" ? "text-primary" : "text-on-surface-variant hover:text-on-surface"
                      }`}
                    >
                      Trends ({detections.length})
                      {activeTab === "detections" && (
                        <motion.div layoutId="activeTabUnderline" className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary" />
                      )}
                    </button>
                    <button
                      onClick={() => setActiveTab("signals")}
                      className={`pb-3 text-sm font-bold transition-all relative ${
                        activeTab === "signals" ? "text-primary" : "text-on-surface-variant hover:text-on-surface"
                      }`}
                    >
                      Raw Signals ({signals.length})
                      {activeTab === "signals" && (
                        <motion.div layoutId="activeTabUnderline" className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary" />
                      )}
                    </button>
                  </div>

                  {isLoading ? (
                    <div className="flex flex-col items-center justify-center py-20 gap-3">
                      <div className="w-8 h-8 rounded-full border-2 border-primary border-t-transparent animate-spin" />
                    </div>
                  ) : activeTab === "detections" ? (
                    detections.length > 0 ? (
                      <motion.div variants={staggerContainer} initial="hidden" animate="visible" className="grid gap-4 md:grid-cols-2">
                        {detections.map((d: any) => (
                          <motion.div key={d.id} variants={staggerItem}>
                            <div 
                              onClick={() => setSelectedDetection(d)}
                              className="bg-surface border border-outline-variant hover:border-primary rounded-xl p-6 cursor-pointer transition-all hover:scale-[1.01] hover:shadow-[0_0_20px_rgba(73,233,224,0.1)] flex flex-col h-full"
                            >
                              <div className="flex justify-between items-start mb-3">
                                <h3 className="font-bold text-lg text-on-surface line-clamp-1">{d.topic}</h3>
                                <span className="bg-surface-variant text-on-surface-variant text-xs px-2 py-1 rounded font-semibold uppercase">{d.stage}</span>
                              </div>
                              <p className="text-sm text-on-surface-variant line-clamp-2 mb-4 flex-grow">
                                {d.description || "No description provided."}
                              </p>
                              <div className="flex justify-between items-center mt-auto pt-4 border-t border-outline-variant">
                                <span className="text-xs text-on-surface-variant flex items-center gap-1">
                                  <Users className="w-4 h-4" /> {d.signal_count}
                                </span>
                                <span className="text-xs font-bold text-primary flex items-center gap-1">
                                  {Math.round(d.confidence * 100)}% Match <ArrowRight className="w-3 h-3" />
                                </span>
                              </div>
                            </div>
                          </motion.div>
                        ))}
                      </motion.div>
                    ) : (
                      <div className="text-center py-20 text-on-surface-variant">No trend clusters found.</div>
                    )
                  ) : (
                    signals.length > 0 ? (
                      <motion.div variants={staggerContainer} initial="hidden" animate="visible" className="space-y-4">
                        {signals.map((s: any) => (
                          <motion.div key={s.id} variants={staggerItem}>
                            <div className="bg-surface border border-outline-variant rounded-xl p-5">
                              <div className="flex items-center gap-2 mb-2">
                                <Radio className="w-4 h-4 text-primary" />
                                <span className="text-xs font-bold text-on-surface uppercase">{s.platform}</span>
                                {s.author && <span className="text-xs text-on-surface-variant">by @{s.author}</span>}
                              </div>
                              <p className="text-sm text-on-surface-variant leading-relaxed">{s.text}</p>
                            </div>
                          </motion.div>
                        ))}
                      </motion.div>
                    ) : (
                      <div className="text-center py-20 text-on-surface-variant">No signals found.</div>
                    )
                  )}
                </>
              ) : (
                <div className="text-center py-20 flex flex-col items-center">
                  <div className="w-16 h-16 rounded-full bg-surface-variant flex items-center justify-center text-primary mb-4">
                    <SearchIcon className="w-8 h-8" />
                  </div>
                  <h3 className="text-lg font-bold text-on-surface mb-2">Begin querying database</h3>
                  <p className="text-sm text-on-surface-variant max-w-sm">Type queries to search clustered trend topics and raw signals across all platforms.</p>
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
}
