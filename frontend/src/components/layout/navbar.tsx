"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Menu, Wallet, X } from "lucide-react";
import { useState } from "react";
import { useAuth } from "@/hooks/use-auth";
import { useTranslations } from "next-intl";
import { Button } from "@/components/ui/button";
import {
  LayoutDashboard,
  ArrowLeftRight,
  PiggyBank,
  Target,
  Bot,
  Settings,
  LogOut,
} from "lucide-react";

function getLocale(pathname: string): string {
  const segments = pathname.split("/").filter(Boolean);
  return segments[0] || "es";
}

export function Navbar() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const pathname = usePathname();
  const locale = getLocale(pathname);
  const { doLogout } = useAuth();
  const t = useTranslations("nav");
  const tCommon = useTranslations("common");

  const navItems = [
    { href: `/${locale}/dashboard`, label: t("dashboard"), icon: LayoutDashboard },
    { href: `/${locale}/transactions`, label: t("transactions"), icon: ArrowLeftRight },
    { href: `/${locale}/budgets`, label: t("budgets"), icon: PiggyBank },
    { href: `/${locale}/goals`, label: t("goals"), icon: Target },
    { href: `/${locale}/chat`, label: t("chat"), icon: Bot },
  ];

  return (
    <header className="md:hidden sticky top-0 z-50 border-b border-border bg-card/80 backdrop-blur-xl px-4 py-3 flex items-center justify-between">
      <div className="flex items-center gap-2">
        <Wallet className="h-5 w-5 text-primary" />
        <span className="font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
          PyStreamFlow
        </span>
      </div>

      <Button variant="ghost" size="icon" onClick={() => setMobileOpen(!mobileOpen)}>
        {mobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
      </Button>

      {mobileOpen && (
        <div className="absolute top-full left-0 right-0 bg-card border-b border-border p-4 shadow-xl">
          <nav className="space-y-1">
            {navItems.map((item) => {
              const isActive = pathname === item.href;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  onClick={() => setMobileOpen(false)}
                  className={`flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all ${
                    isActive ? "bg-primary/10 text-primary" : "text-muted-foreground hover:bg-secondary"
                  }`}
                >
                  <item.icon className="h-5 w-5" />
                  {item.label}
                </Link>
              );
            })}
          </nav>
          <div className="border-t border-border mt-3 pt-3 flex flex-col gap-1">
            <Link
              href={`/${locale}/settings`}
              onClick={() => setMobileOpen(false)}
              className="flex items-center gap-3 rounded-lg px-3 py-2 text-sm text-muted-foreground hover:bg-secondary"
            >
              <Settings className="h-4 w-4" />
              {t("settings")}
            </Link>
            <button
              onClick={() => { doLogout(); setMobileOpen(false); }}
              className="flex items-center gap-3 rounded-lg px-3 py-2 text-sm text-destructive hover:bg-destructive/10"
            >
              <LogOut className="h-4 w-4" />
              {tCommon("logout")}
            </button>
          </div>
        </div>
      )}
    </header>
  );
}
