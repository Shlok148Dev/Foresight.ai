"use client";

import React from "react";
import { motion } from "framer-motion";
import clsx from "clsx";

interface CardProps {
  children: React.ReactNode;
  className?: string;
  hover?: boolean;
  glow?: boolean;
  padding?: "sm" | "md" | "lg";
  onClick?: () => void;
}

export function Card({
  children,
  className,
  hover = true,
  glow = false,
  padding = "md",
  onClick
}: CardProps) {
  const paddings = { sm: "p-4", md: "p-6", lg: "p-8" };

  return (
    <motion.div
      onClick={onClick}
      whileHover={hover ? { scale: 1.01 } : undefined}
      transition={{ type: "spring", stiffness: 300, damping: 25 }}
      className={clsx(
        "rounded-xl border border-outline-variant bg-surface transition-colors duration-300",
        hover && "hover:border-primary hover:shadow-[0_0_20px_rgba(73,233,224,0.1)] cursor-pointer",
        glow && "border-primary/30 shadow-[0_0_20px_rgba(73,233,224,0.1)]",
        paddings[padding],
        className
      )}
    >
      {children}
    </motion.div>
  );
}

/* ── Stat Card variant ─────────────────────────────────────────── */

interface StatCardProps {
  label: string;
  value: string | number;
  change?: string;
  trend?: "up" | "down" | "neutral";
  icon?: React.ReactNode;
}

export function StatCard({ label, value, change, trend, icon }: StatCardProps) {
  const trendColor =
    trend === "up"
      ? "text-primary"
      : trend === "down"
      ? "text-error"
      : "text-on-surface-variant";

  return (
    <Card className="space-y-2 flex flex-col gap-1">
      <div className="flex items-center justify-between text-on-surface-variant">
        <p className="font-label-caps text-xs uppercase font-bold tracking-wider">{label}</p>
        {icon && <span className="text-on-surface-variant">{icon}</span>}
      </div>
      <p className="font-headline-lg text-3xl font-bold text-on-surface">{value}</p>
      {change && (
        <p className={clsx("font-body-sm text-sm flex items-center gap-1", trendColor)}>
          {trend === "up" && "↑ "}
          {trend === "down" && "↓ "}
          {change}
        </p>
      )}
    </Card>
  );
}
