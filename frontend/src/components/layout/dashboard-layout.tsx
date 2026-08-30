"use client";

import { Sidebar } from "./sidebar";
import { Navbar } from "./navbar";
import { useKeyboardShortcuts } from "@/hooks/use-keyboard-shortcuts";

export function DashboardLayout({ children }: { children: React.ReactNode }) {
  useKeyboardShortcuts();

  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar />
      <Navbar />
      <main className="flex-1 lg:ml-64 p-4 md:p-8 overflow-y-auto">
        {children}
      </main>
    </div>
  );
}
