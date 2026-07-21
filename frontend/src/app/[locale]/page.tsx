"use client";

import { useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";
import { useAuthStore } from "@/lib/auth";

function getLocale(pathname: string): string {
  const segments = pathname.split("/").filter(Boolean);
  return segments[0] || "es";
}

export default function Home() {
  const router = useRouter();
  const pathname = usePathname();
  const locale = getLocale(pathname);
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);

  useEffect(() => {
    if (isAuthenticated) {
      router.replace(`/${locale}/dashboard`);
    } else {
      router.replace(`/${locale}/login`);
    }
  }, [isAuthenticated, router, locale]);

  return (
    <div className="flex h-screen items-center justify-center">
      <div className="h-8 w-8 animate-spin rounded-full border-2 border-primary border-t-transparent" />
    </div>
  );
}
