"use client";

import { useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import { useLocale } from "next-intl";

interface ShortcutMap {
  [key: string]: () => void;
}

export function useKeyboardShortcuts(shortcuts?: ShortcutMap) {
  const router = useRouter();
  const locale = useLocale();

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
