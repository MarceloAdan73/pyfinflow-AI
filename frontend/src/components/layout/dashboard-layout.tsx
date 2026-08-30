"use client";

import { Sidebar } from "./sidebar";
import { Navbar } from "./navbar";
import { BottomNav } from "./bottom-nav";
import { useKeyboardShortcuts } from "@/hooks/use-keyboard-shortcuts";

export function DashboardLayout({ children }: { children: React.ReactNode }) {
  useKeyboardShortcuts();

  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar />
      <div className="flex-1 lg:ml-64 flex flex-col min-w-0">
        <Navbar />
        <main className="flex-1 p-4 pb-24 md:p-8 md:pb-8 min-w-0 w-full overflow-x-hidden">
          {children}
        </main>
      </div>
      <BottomNav />
    </div>
  );
}
