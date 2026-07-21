"use client";

import { useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";
import { useAuthStore } from "@/lib/auth";
import { api } from "@/lib/api";
import type { User } from "@/types";

function getLocale(pathname: string): string {
  const segments = pathname.split("/").filter(Boolean);
  return segments[0] || "es";
}

export function useAuth() {
  const { user, tokens, isAuthenticated, login, setUser, logout } = useAuthStore();
  const router = useRouter();
  const pathname = usePathname();
  const locale = getLocale(pathname);

  useEffect(() => {
    if (isAuthenticated && !user && tokens?.access_token) {
      api<User>("/auth/me", { token: tokens.access_token })
        .then((u) => setUser(u))
        .catch(() => {
          logout();
          router.push(`/${locale}/login`);
        });
    }
  }, [isAuthenticated, user, tokens, setUser, logout, router, locale]);

  const doLogin = async (username: string, password: string) => {
    const data = await api<{ access_token: string; refresh_token: string; token_type: string }>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ username, password }),
    });
    const userRes = await api<User>("/auth/me", { token: data.access_token });
    login(data, userRes);
    return userRes;
  };

  const doRegister = async (username: string, password: string) => {
    const data = await api<{ access_token: string; refresh_token: string; token_type: string }>("/auth/register", {
      method: "POST",
      body: JSON.stringify({ username, password }),
    });
    const userRes = await api<User>("/auth/me", { token: data.access_token });
    login(data, userRes);
    return userRes;
  };

  const doLogout = () => {
    logout();
    router.push(`/${locale}/login`);
  };

  return { user, isAuthenticated, doLogin, doRegister, doLogout };
}
