"use client";

import Link from "next/link";
import { useLocale } from "next-intl";
import { Logo } from "@/components/ui/logo";
import { Settings } from "lucide-react";

export function Navbar() {
  const locale = useLocale();

  return (
    <header className="lg:hidden sticky top-0 z-40 border-b border-border bg-card/80 backdrop-blur-xl px-4 py-3 flex items-center justify-between">
      <Logo href={`/${locale}/dashboard`} size="sm" />
      <Link
        href={`/${locale}/settings`}
        aria-label="Ajustes"
        className="inline-flex h-10 w-10 items-center justify-center rounded-lg text-muted-foreground hover:bg-secondary hover:text-foreground transition-colors"
      >
        <Settings className="h-5 w-5" />
      </Link>
    </header>
  );
}
