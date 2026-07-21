"use client";

import { useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";
import { useAuthStore } from "@/lib/auth";

export function AuthGuard({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);

  const segments = pathname.split("/").filter(Boolean);
  const locale = segments[0];
  const pathWithoutLocale = "/" + segments.slice(1).join("/");
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
