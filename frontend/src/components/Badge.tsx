"use client";

import React from "react";
import clsx from "clsx";

type BadgeVariant = "primary" | "success" | "warning" | "error" | "muted" | "info";

interface BadgeProps {
  children: React.ReactNode;
  variant?: BadgeVariant;
  size?: "sm" | "md" | "lg";
  icon?: React.ReactNode;
  pulse?: boolean;
}

const variantStyles: Record<BadgeVariant, string> = {
  primary: "bg-primary/20 text-primary border-primary/30",
  success: "bg-tertiary-container/20 text-tertiary-container border-tertiary-container/30", // Using tertiary as 'success' in this theme
  warning: "bg-tertiary/20 text-tertiary border-tertiary/30",
  error: "bg-error/20 text-error border-error/30",
  muted: "bg-surface-variant text-on-surface-variant border-outline-variant",
  info: "bg-secondary/20 text-secondary border-secondary/30",
};

export function Badge({
  children,
  variant = "primary",
  size = "md",
  icon,
  pulse = false,
}: BadgeProps) {
  const sizes = {
    sm: "px-2 py-0.5 text-[10px] uppercase font-bold tracking-wider",
    md: "px-2.5 py-1 text-xs uppercase font-bold tracking-wider",
    lg: "px-3 py-1.5 text-sm uppercase font-bold tracking-wider",
  };

  return (
    <span
      className={clsx(
        "inline-flex items-center gap-1.5 rounded-md border",
        variantStyles[variant],
        sizes[size]
      )}
    >
      {pulse && (
        <span className="relative flex h-1.5 w-1.5">
          <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-current opacity-75" />
          <span className="relative inline-flex h-1.5 w-1.5 rounded-full bg-current" />
        </span>
      )}
      {icon}
      {children}
    </span>
  );
}
