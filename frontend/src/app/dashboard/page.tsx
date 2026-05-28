"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";

import {
  TrendingUp as TrendingUpIcon, Activity as ActivityIcon, Bell as BellIcon, CheckCircle as CheckCircleIcon, Cpu as CpuIcon, Sparkles as SparklesIcon, Rocket as RocketIcon, Download as DownloadIcon
} from "lucide-react";
import { Sidebar } from "@/components";
import { useAuth } from "@/hooks/useAuth";
import { useDetections, useStagesSummary } from "@/hooks/useSignals";
import { staggerContainer, staggerItem } from "@/lib/animations";

export default function DashboardPage() {
  const router = useRouter();
  const { user, loadUser, token } = useAuth();
  const { data: detections, isLoading: detectionsLoading } = useDetections({
    limit: 10,
    sort_by: "confidence",
  });
  const { data: summary } = useStagesSummary();

  /* Load user on mount */
  useEffect(() => {
    if (!token) {
      router.push("/login");
      return;
    }
    if (!user) loadUser();
  }, [token, user, loadUser, router]);

  const totalDetections = summary?.total || 0;
  const stages = summary?.stages || {};
  const activeTrends = (stages.accelerating || 0) + (stages.peaking || 0);

  return (
    <div className="bg-background text-on-surface antialiased min-h-screen flex flex-col md:flex-row font-body-md overflow-x-hidden selection:bg-primary-container selection:text-on-primary-container">
      <Sidebar />

      {/* TopAppBar */}
      <header className="fixed top-0 right-0 w-[calc(100%-240px)] z-30 bg-surface/80 backdrop-blur-xl border-b border-outline-variant flex justify-between items-center h-16 px-lg transition-all duration-200 hidden md:flex">
        <div className="flex-1 max-w-md relative">
           {/* Top bar can be empty or have global search */}
        </div>
        <div className="flex items-center gap-md text-on-surface-variant">
          <button className="hover:text-primary transition-colors p-sm rounded-full hover:bg-surface-variant relative">
            <BellIcon className="w-5 h-5" />
            <span className="absolute top-2 right-2 w-2 h-2 bg-primary rounded-full"></span>
          </button>
        </div>
      </header>

      {/* Mobile TopAppBar */}
      <header className="md:hidden flex justify-between items-center px-md py-sm border-b border-outline-variant bg-surface/80 backdrop-blur-xl sticky top-0 z-40">
        <div className="flex items-center gap-xs">
          <span className="text-headline-sm font-bold text-primary">Foresight</span>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 md:ml-[240px] pt-8 md:pt-[88px] px-md md:px-xl pb-xl min-h-screen max-w-container-max mx-auto w-full">
        <div className="mb-lg flex justify-between items-end">
          <div>
            <h1 className="font-headline-md text-3xl font-bold text-on-surface mb-xs">Dashboard Overview</h1>
            <p className="font-body-sm text-sm text-on-surface-variant">High-level account and platform activity summary.</p>
          </div>
          <button className="hidden md:flex items-center gap-xs text-primary font-body-sm text-sm hover:underline font-semibold">
            <DownloadIcon className="w-4 h-4" /> Export Report
          </button>
        </div>

        {/* Trend Health KPIs */}
        <motion.div variants={staggerContainer} initial="hidden" animate="visible" className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-md mb-lg">
          {/* KPI 1 */}
          <motion.div variants={staggerItem} className="bg-surface border border-outline-variant rounded-xl p-md flex flex-col gap-xs interactive-card">
            <div className="flex justify-between items-center text-on-surface-variant mb-xs">
              <span className="font-label-caps text-xs uppercase font-bold tracking-wider">Total Detections</span>
              <ActivityIcon className="w-5 h-5" />
            </div>
            <div className="font-headline-lg text-3xl font-bold text-on-surface">{totalDetections}</div>
            <div className="font-body-sm text-sm text-primary flex items-center gap-1">
              <TrendingUpIcon className="w-4 h-4" /> Real-time active DB
            </div>
          </motion.div>

          {/* KPI 2 */}
          <motion.div variants={staggerItem} className="bg-surface border border-outline-variant rounded-xl p-md flex flex-col gap-xs interactive-card">
            <div className="flex justify-between items-center text-on-surface-variant mb-xs">
              <span className="font-label-caps text-xs uppercase font-bold tracking-wider">Active Trends</span>
              <BellIcon className="w-5 h-5" />
            </div>
            <div className="font-headline-lg text-3xl font-bold text-on-surface">{activeTrends}</div>
            <div className="font-body-sm text-sm text-error flex items-center gap-1">
              <ActivityIcon className="w-4 h-4" /> Accelerating/Peaking
            </div>
          </motion.div>

          {/* KPI 3 */}
          <motion.div variants={staggerItem} className="bg-surface border border-outline-variant rounded-xl p-md flex flex-col gap-xs interactive-card">
            <div className="flex justify-between items-center text-on-surface-variant mb-xs">
              <span className="font-label-caps text-xs uppercase font-bold tracking-wider">Avg Confidence</span>
              <CheckCircleIcon className="w-5 h-5" />
            </div>
            <div className="font-headline-lg text-3xl font-bold text-on-surface">
              {detections?.detections?.length ? Math.round(detections.detections[0].confidence * 100) : 0}%
            </div>
            <div className="font-body-sm text-sm text-primary flex items-center gap-1">
              <TrendingUpIcon className="w-4 h-4" /> Top prediction accuracy
            </div>
          </motion.div>

          {/* KPI 4 */}
          <motion.div variants={staggerItem} className="bg-surface border border-outline-variant rounded-xl p-md flex flex-col gap-xs interactive-card">
            <div className="flex justify-between items-center text-on-surface-variant mb-xs">
              <span className="font-label-caps text-xs uppercase font-bold tracking-wider">Stage Diversity</span>
              <TrendingUpIcon className="w-5 h-5" />
            </div>
            <div className="font-headline-lg text-3xl font-bold text-on-surface">5</div>
            <div className="font-body-sm text-sm text-tertiary-container flex items-center gap-1">
              Pipeline saturation
            </div>
          </motion.div>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-lg mb-lg">
          {/* Market Sentiment (Stage Pipeline mock) */}
          <div className="bg-surface border border-outline-variant rounded-xl p-lg flex flex-col gap-md">
            <h2 className="font-headline-sm text-xl font-bold text-on-surface border-b border-outline-variant/50 pb-sm">Trend Pipeline</h2>
            <div className="flex flex-col gap-sm mt-2">
              {[
                { name: "Embryonic", count: stages.embryonic || 0, color: "bg-surface-variant" },
                { name: "Emerging", count: stages.emerging || 0, color: "bg-primary" },
                { name: "Accelerating", count: stages.accelerating || 0, color: "bg-tertiary-container" },
                { name: "Peaking", count: stages.peaking || 0, color: "bg-error" },
                { name: "Declining", count: stages.declining || 0, color: "bg-secondary" },
              ].map((stage) => {
                const max = totalDetections > 0 ? totalDetections : 1;
                const percentage = Math.round((stage.count / max) * 100);
                return (
                  <div key={stage.name} className="flex flex-col gap-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-on-surface">{stage.name}</span>
                      <span className="font-bold text-on-surface">{stage.count} ({percentage}%)</span>
                    </div>
                    <div className="w-full bg-background rounded-full h-2 border border-outline-variant">
                      <div className={`${stage.color} h-2 rounded-full`} style={{ width: `${percentage}%` }}></div>
                    </div>
                  </div>
                )
              })}
            </div>
          </div>

          {/* Top Performers */}
          <div className="bg-surface border border-outline-variant rounded-xl p-lg flex flex-col gap-md">
            <h2 className="font-headline-sm text-xl font-bold text-on-surface border-b border-outline-variant/50 pb-sm">Top Detections</h2>
            <div className="flex flex-col gap-2 flex-grow overflow-y-auto max-h-[300px] pr-2">
              {detectionsLoading ? (
                 <div className="flex justify-center items-center h-full">
                    <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin"></div>
                 </div>
              ) : detections?.detections?.length ? (
                detections.detections.slice(0, 5).map((d: any, i: number) => {
                  const icons = [CpuIcon, SparklesIcon, RocketIcon];
                  const Icon = icons[i % icons.length];
                  const colors = ["text-primary", "text-tertiary-container", "text-error", "text-secondary", "text-on-surface"];
                  const bgColors = ["bg-primary/20", "bg-tertiary-container/20", "bg-error/20", "bg-secondary/20", "bg-surface-variant"];
                  
                  return (
                    <div key={d.id} className="flex items-center justify-between p-3 rounded-lg hover:bg-surface-variant transition-colors cursor-pointer">
                      <div className="flex items-center gap-4">
                        <div className={`w-10 h-10 rounded-full flex items-center justify-center ${bgColors[i % 5]} ${colors[i % 5]}`}>
                          <Icon className="w-5 h-5" />
                        </div>
                        <div>
                          <div className="font-bold text-sm text-on-surface line-clamp-1">{d.topic}</div>
                          <div className="text-xs text-on-surface-variant uppercase">{d.stage}</div>
                        </div>
                      </div>
                      <div className={`text-lg font-bold ${colors[i % 5]}`}>
                        {Math.round(d.confidence * 100)}%
                      </div>
                    </div>
                  );
                })
              ) : (
                <div className="text-center py-10 text-on-surface-variant text-sm">No detections available.</div>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
