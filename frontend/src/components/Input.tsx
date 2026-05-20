"use client";

import React, { forwardRef } from "react";
import clsx from "clsx";

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  icon?: React.ReactNode;
  helperText?: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, icon, helperText, className, id, ...props }, ref) => {
    const inputId = id || label?.toLowerCase().replace(/\s+/g, "-");

    return (
      <div className="w-full">
        {label && (
          <label
            htmlFor={inputId}
            className="mb-2 block font-body-sm text-sm font-semibold text-on-surface-variant"
          >
            {label}
          </label>
        )}
        <div className="relative">
          {icon && (
            <div className="pointer-events-none absolute left-3.5 top-1/2 -translate-y-1/2 text-on-surface-variant">
              {icon}
            </div>
          )}
          <input
            ref={ref}
            id={inputId}
            className={clsx(
              "w-full rounded-lg border bg-surface px-4 py-3 font-body-md text-on-surface placeholder:text-on-surface-variant/50 transition-all duration-200",
              "focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary",
              icon && "pl-11",
              error
                ? "border-error bg-error/5"
                : "border-outline-variant hover:border-outline",
              className
            )}
            {...props}
          />
        </div>
        {error && (
          <p className="mt-1.5 font-body-sm text-xs font-medium text-error">{error}</p>
        )}
        {helperText && !error && (
          <p className="mt-1.5 font-body-sm text-xs text-on-surface-variant">{helperText}</p>
        )}
      </div>
    );
  }
);

Input.displayName = "Input";
