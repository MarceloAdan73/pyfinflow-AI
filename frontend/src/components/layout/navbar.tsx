"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Menu, X } from "lucide-react";
import { useState } from "react";
import { useAuth } from "@/hooks/use-auth";
import { useLocale, useTranslations } from "next-intl";
import { Button } from "@/components/ui/button";
import { Logo } from "@/components/ui/logo";
import { ThemeToggle } from "@/components/ui/theme-toggle";
import { LanguageSelector } from "@/components/ui/language-selector";
import {
  LayoutDashboard,
  ArrowLeftRight,
  PiggyBank,
  Target,
  Bot,
  Settings,
  LogOut,
} from "lucide-react";

export function Navbar() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const pathname = usePathname();
  const locale = useLocale();
  const { user, doLogout } = useAuth();
  const t = useTranslations("nav");

  const navItems = [
    { href: `/${locale}/dashboard`, label: t("dashboard"), icon: LayoutDashboard },
    { href: `/${locale}/transactions`, label: t("transactions"), icon: ArrowLeftRight },
    { href: `/${locale}/budgets`, label: t("budgets"), icon: PiggyBank },
    { href: `/${locale}/goals`, label: t("goals"), icon: Target },
    { href: `/${locale}/chat`, label: t("chat"), icon: Bot },
  ];

  const isActive = (href: string) => pathname === href || pathname.startsWith(href + "/");

  return (
    <>
      <header className="md:hidden sticky top-0 z-50 border-b border-border bg-card/80 backdrop-blur-xl px-4 py-3 flex items-center justify-between">
        <div className="flex items-center">
          <Logo href={`/${locale}/dashboard`} size="sm" />
        </div>

        <Button variant="ghost" size="icon" aria-label="Abrir menú" onClick={() => setMobileOpen(true)}>
          <Menu className="h-5 w-5" />
        </Button>
      </header>

      {mobileOpen && (
        <div className="fixed inset-0 z-50 md:hidden">
          <div
            className="fixed inset-0 bg-black/60 backdrop-blur-sm"
            onClick={() => setMobileOpen(false)}
          />
          <aside className="fixed top-0 left-0 bottom-0 w-64 bg-card border-r border-border p-4 flex flex-col shadow-2xl overflow-y-auto">
            <div className="flex items-center justify-between mb-6">
              <Logo size="md" />
              <Button variant="ghost" size="icon" aria-label="Cerrar menú" onClick={() => setMobileOpen(false)}>
                <X className="h-5 w-5" />
              </Button>
            </div>

            <nav className="flex-1 space-y-1">
              {navItems.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  onClick={() => setMobileOpen(false)}
                  className={`flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all ${
                    isActive(item.href) ? "bg-primary/10 text-primary" : "text-muted-foreground hover:bg-secondary hover:text-foreground"
                  }`}
                >
                  <item.icon className="h-5 w-5 shrink-0" />
                  {item.label}
                </Link>
              ))}
            </nav>

            <div className="border-t border-border pt-3 mt-3">
              <div className="flex items-center gap-2 px-2 mb-3">
                <div className="h-8 w-8 rounded-full bg-primary/20 flex items-center justify-center text-sm font-semibold text-primary shrink-0">
                  {user?.username?.[0]?.toUpperCase() || "U"}
                </div>
                <span className="text-sm font-medium truncate flex-1">{user?.username}</span>
              </div>
              <div className="flex items-center justify-start gap-2 px-2 mb-3">
                <LanguageSelector />
                <ThemeToggle />
              </div>
              <Link
                href={`/${locale}/settings`}
                onClick={() => setMobileOpen(false)}
                className={`flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium ${
                  isActive(`/${locale}/settings`)
                    ? "bg-primary/10 text-primary"
                    : "text-muted-foreground hover:bg-secondary hover:text-foreground"
                }`}
              >
                <Settings className="h-4 w-4" />
                {t("settings")}
              </Link>
              <button
                onClick={() => { doLogout(); setMobileOpen(false); }}
                className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-muted-foreground hover:bg-destructive/10 hover:text-destructive"
              >
                <LogOut className="h-4 w-4" />
                {t("logout")}
              </button>
            </div>
          </aside>
        </div>
      )}
    </>
  );
}
