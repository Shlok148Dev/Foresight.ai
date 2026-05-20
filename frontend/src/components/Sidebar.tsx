"use client";

import React from "react";
import { useRouter, usePathname } from "next/navigation";
import Link from "next/link";
import {
  Rss, Search, LayoutDashboard, Bookmark, Settings, LogOut, User as UserIcon
} from "lucide-react";
import { useAuth } from "@/hooks/useAuth";

export function Sidebar() {
  const { user, logout } = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  const handleLogout = () => {
    logout();
    router.push("/login");
  };

  const navItems = [
    { icon: Rss, label: "Feed", href: "/feed" },
    { icon: Search, label: "Search", href: "/search" },
    { icon: LayoutDashboard, label: "Dashboard", href: "/dashboard" },
    { icon: Bookmark, label: "Saved", href: "/saved" },
    { icon: Settings, label: "Settings", href: "/settings" },
  ];

  return (
    <>
      {/* Desktop Sidebar */}
      <nav className="hidden md:flex flex-col h-full w-[240px] fixed left-0 top-0 bg-surface border-r border-outline-variant py-lg px-md z-40 font-body-md">
        <div className="mb-xl">
          <h1 className="font-headline-sm text-headline-sm font-bold text-primary">Foresight</h1>
          <p className="font-label-caps text-xs text-on-surface-variant uppercase tracking-wider mt-1">Predictive Intel</p>
        </div>
        <ul className="flex flex-col gap-sm flex-grow">
          {navItems.map((item) => {
            const active = pathname === item.href;
            return (
              <li key={item.label}>
                <Link
                  href={item.href}
                  className={`flex items-center gap-md px-md py-sm rounded-lg transition-colors duration-200 ${
                    active 
                      ? "text-primary font-bold border-r-2 border-primary bg-surface-variant/50" 
                      : "text-on-surface-variant hover:bg-surface-variant"
                  }`}
                >
                  <item.icon className="w-5 h-5" />
                  <span className="font-body-md text-body-md">{item.label}</span>
                </Link>
              </li>
            );
          })}
        </ul>
        
        <div className="mt-auto border-t border-outline-variant pt-md flex flex-col gap-2">
          {user && (
             <div className="flex items-center gap-3 px-2 py-2 mb-2">
               <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary-container text-background font-bold uppercase">
                 {user.username?.charAt(0) || "U"}
               </div>
               <div className="flex-1 min-w-0">
                 <p className="truncate text-sm font-bold text-on-surface">
                   {user.username}
                 </p>
               </div>
             </div>
          )}
          
          <Link href="/profile" className="flex items-center gap-md px-md py-sm rounded-lg text-on-surface-variant hover:bg-surface-variant transition-colors duration-200">
            <UserIcon className="w-5 h-5" />
            <span className="font-body-md text-body-md">Profile</span>
          </Link>
          <button onClick={handleLogout} className="flex w-full items-center gap-md px-md py-sm rounded-lg text-on-surface-variant hover:bg-error/20 hover:text-error transition-colors duration-200">
            <LogOut className="w-5 h-5" />
            <span className="font-body-md text-body-md">Log Out</span>
          </button>
        </div>
      </nav>

      {/* Mobile Bottom Navigation */}
      <nav className="md:hidden fixed bottom-0 left-0 right-0 h-16 bg-surface border-t border-outline-variant flex justify-around items-center z-50">
        {navItems.slice(0, 4).map((item) => {
          const active = pathname === item.href;
          return (
            <Link key={item.label} href={item.href} className={`flex flex-col items-center p-sm transition-colors ${active ? "text-primary font-bold" : "text-on-surface-variant hover:text-primary"}`}>
              <item.icon className="w-6 h-6" />
            </Link>
          )
        })}
      </nav>
    </>
  );
}

export default Sidebar;
