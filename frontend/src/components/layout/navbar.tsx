"use client";

import { useLocale, useTranslations } from "next-intl";
import { Logo } from "@/components/ui/logo";
import { ThemeToggle } from "@/components/ui/theme-toggle";
import { LogOut } from "lucide-react";
import { useAuth } from "@/hooks/use-auth";

export function Navbar() {
  const locale = useLocale();
  const { doLogout } = useAuth();
  const t = useTranslations("nav");

  return (
    <header className="lg:hidden sticky top-0 z-40 border-b border-border bg-card/80 backdrop-blur-xl px-4 py-3 flex items-center justify-between">
      <Logo href={`/${locale}/dashboard`} size="sm" />
      <div className="flex items-center gap-1">
        <ThemeToggle />
        <button
          onClick={doLogout}
          aria-label={t("logout")}
          title={t("logout")}
          className="inline-flex h-10 w-10 items-center justify-center rounded-lg text-muted-foreground hover:bg-destructive/10 hover:text-destructive transition-colors"
        >
          <LogOut className="h-5 w-5" />
        </button>
      </div>
    </header>
  );
}
