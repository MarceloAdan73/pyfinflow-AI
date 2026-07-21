"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/lib/auth";
import { api } from "@/lib/api";
import type { User } from "@/types";

export function useAuth() {
  const { user, tokens, isAuthenticated, login, setUser, logout } = useAuthStore();
  const router = useRouter();

  useEffect(() => {
    if (isAuthenticated && !user && tokens?.access_token) {
      api<User>("/auth/me", { token: tokens.access_token })
        .then((u) => setUser(u))
        .catch(() => {
          logout();
          router.push("/login");
        });
    }
  }, [isAuthenticated, user, tokens, setUser, logout, router]);

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
    router.push("/login");
  };

  return { user, isAuthenticated, doLogin, doRegister, doLogout };
}
