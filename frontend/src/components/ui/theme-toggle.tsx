"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Sun, Moon } from "lucide-react";
import { useTranslations } from "next-intl";

function getInitialTheme(): boolean {
  if (typeof window === "undefined") return true;
  try {
    return localStorage.getItem("theme") !== "light";
  } catch {
    return true;
  }
}

export function ThemeToggle() {
  const t = useTranslations("common");
  const [dark, setDark] = useState(getInitialTheme);

  const toggle = () => {
    const next = !dark;
    setDark(next);
    const root = document.documentElement;
    if (next) {
      root.classList.add("dark");
      root.classList.remove("light");
    } else {
      root.classList.remove("dark");
      root.classList.add("light");
    }
    localStorage.setItem("theme", next ? "dark" : "light");
  };

  return (
    <Button
      variant="ghost"
      size="icon"
      onClick={toggle}
      className="h-9 w-9"
      title={dark ? t("lightMode") : t("darkMode")}
    >
      {dark ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
    </Button>
  );
}
