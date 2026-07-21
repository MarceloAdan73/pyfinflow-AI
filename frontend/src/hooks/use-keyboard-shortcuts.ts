"use client";

import { useEffect, useCallback } from "react";
import { useRouter, usePathname } from "next/navigation";

function getLocale(pathname: string): string {
  const segments = pathname.split("/").filter(Boolean);
  return segments[0] || "es";
}

interface ShortcutMap {
  [key: string]: () => void;
}

export function useKeyboardShortcuts(shortcuts?: ShortcutMap) {
  const router = useRouter();
  const pathname = usePathname();
  const locale = getLocale(pathname);

  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      const isInput = e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement;
      if (isInput) return;

      const key = [
        e.ctrlKey || e.metaKey ? "Ctrl" : "",
        e.shiftKey ? "Shift" : "",
        e.altKey ? "Alt" : "",
        e.key.toLowerCase(),
      ]
        .filter(Boolean)
        .join("+");

      if (shortcuts?.[key]) {
        e.preventDefault();
        shortcuts[key]();
        return;
      }

      switch (key) {
        case "Ctrl+d":
          e.preventDefault();
          router.push(`/${locale}/dashboard`);
          break;
        case "Ctrl+t":
          e.preventDefault();
          router.push(`/${locale}/transactions`);
          break;
        case "Ctrl+b":
          e.preventDefault();
          router.push(`/${locale}/budgets`);
          break;
        case "Ctrl+g":
          e.preventDefault();
          router.push(`/${locale}/goals`);
          break;
        case "Ctrl+i":
          e.preventDefault();
          router.push(`/${locale}/chat`);
          break;
        case "Ctrl+,": // Ctrl + comma → settings
          e.preventDefault();
          router.push(`/${locale}/settings`);
          break;
      }
    },
    [router, shortcuts, locale]
  );

  useEffect(() => {
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [handleKeyDown]);
}
