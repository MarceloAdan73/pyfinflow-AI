"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useLocale, useTranslations } from "next-intl";
import {
  LayoutDashboard,
  ArrowLeftRight,
  PiggyBank,
  Target,
  Bot,
} from "lucide-react";

export function BottomNav() {
  const pathname = usePathname();
  const locale = useLocale();
  const t = useTranslations("nav");

  const items = [
    { href: `/${locale}/dashboard`, label: t("dashboard"), icon: LayoutDashboard },
    { href: `/${locale}/transactions`, label: t("transactions"), icon: ArrowLeftRight },
    { href: `/${locale}/budgets`, label: t("budgets"), icon: PiggyBank },
    { href: `/${locale}/goals`, label: t("goals"), icon: Target },
    { href: `/${locale}/chat`, label: t("chat"), icon: Bot },
  ];

  const isActive = (href: string) => pathname === href || pathname.startsWith(href + "/");

  return (
    <nav className="lg:hidden fixed bottom-0 left-0 right-0 z-40 border-t border-border bg-card/90 backdrop-blur-xl pb-[env(safe-area-inset-bottom)]">
      <div className="grid grid-cols-5">
        {items.map((item) => {
          const active = isActive(item.href);
          return (
            <Link
              key={item.href}
              href={item.href}
              className="flex flex-col items-center justify-center gap-1 py-2.5 text-[10px] font-medium transition-colors"
            >
              <item.icon
                className={`h-5 w-5 transition-colors ${
                  active ? "text-primary" : "text-muted-foreground"
                }`}
              />
              <span className={active ? "text-primary" : "text-muted-foreground"}>
                {item.label}
              </span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
