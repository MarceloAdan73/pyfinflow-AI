"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import {
  LayoutDashboard,
  ArrowLeftRight,
  PiggyBank,
  Target,
  Bot,
  Settings,
  LogOut,
  Wallet,
} from "lucide-react";
import { useAuth } from "@/hooks/use-auth";
import { ThemeToggle } from "@/components/ui/theme-toggle";
import { LanguageSelector } from "@/components/ui/language-selector";
import { useLocale, useTranslations } from "next-intl";

export function Sidebar() {
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

  return (
    <aside className="hidden md:flex flex-col w-64 h-screen border-r border-border bg-card/50 backdrop-blur-xl p-4 fixed left-0 top-0 z-40">
      <div className="flex items-center gap-2 mb-8 px-2">
        <Wallet className="h-7 w-7 text-primary" />
        <span className="text-lg font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
          PyStreamFlow
        </span>
      </div>

      <nav className="flex-1 space-y-1">
        {navItems.map((item) => {
          const isActive = pathname === item.href || pathname.startsWith(item.href + "/");
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all duration-200",
                isActive
                  ? "bg-primary/10 text-primary"
                  : "text-muted-foreground hover:bg-secondary hover:text-foreground"
              )}
            >
              <item.icon className="h-5 w-5 shrink-0" />
              {item.label}
            </Link>
          );
        })}
      </nav>

      <div className="border-t border-border pt-4 mt-4">
        <div className="flex items-center gap-2 px-2 mb-3">
          <div className="h-8 w-8 rounded-full bg-primary/20 flex items-center justify-center text-sm font-semibold text-primary shrink-0">
            {user?.username?.[0]?.toUpperCase() || "U"}
          </div>
          <span className="text-sm font-medium truncate flex-1">{user?.username}</span>
          <LanguageSelector />
          <ThemeToggle />
        </div>
        <div className="space-y-1">
          <Link
            href={`/${locale}/settings`}
            className={cn(
              "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-all",
              pathname === `/${locale}/settings`
                ? "bg-primary/10 text-primary"
                : "text-muted-foreground hover:bg-secondary hover:text-foreground"
            )}
          >
            <Settings className="h-4 w-4" />
            {t("settings")}
          </Link>
          <button
            onClick={doLogout}
            className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-muted-foreground hover:bg-destructive/10 hover:text-destructive transition-all"
          >
            <LogOut className="h-4 w-4" />
            {t("logout")}
          </button>
        </div>
      </div>
    </aside>
  );
}
