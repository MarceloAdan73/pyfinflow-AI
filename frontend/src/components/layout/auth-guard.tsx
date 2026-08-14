"use client";

import { useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";
import { useLocale } from "next-intl";
import { useAuthStore } from "@/lib/auth";
import { locales } from "@/i18n/config";

export function AuthGuard({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const locale = useLocale();
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);

  const segments = pathname.split("/").filter(Boolean);
  const hasPrefix = locales.includes(segments[0] as (typeof locales)[number]);
  const pathWithoutLocale = "/" + (hasPrefix ? segments.slice(1) : segments).join("/");
  const isPublicPath = ["/login", "/register"].includes(pathWithoutLocale);

  useEffect(() => {
    if (!isAuthenticated && !isPublicPath) {
      router.replace(`/${locale}/login`);
    }
  }, [isAuthenticated, isPublicPath, locale, router]);

  if (!isAuthenticated && !isPublicPath) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-primary border-t-transparent" />
      </div>
    );
  }

  return <>{children}</>;
}
