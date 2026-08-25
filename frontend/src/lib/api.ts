const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface ApiOptions extends RequestInit {
  token?: string;
}

let isRefreshing = false;
let refreshPromise: Promise<string | null> | null = null;

async function refreshAccessToken(): Promise<string | null> {
  try {
    const stored = localStorage.getItem("auth-storage");
    if (!stored) return null;
    const { state } = JSON.parse(stored);
    const refreshToken = state?.tokens?.refresh_token;
    if (!refreshToken) return null;

    const res = await fetch(`${API_URL}/auth/refresh`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });

    if (!res.ok) return null;

    const data = await res.json();
    const newTokens = {
      ...state.tokens,
      access_token: data.access_token,
    };
    localStorage.setItem(
      "auth-storage",
      JSON.stringify({ ...state, tokens: newTokens })
    );
    return data.access_token;
  } catch {
    return null;
  }
}

export async function api<T>(path: string, options: ApiOptions = {}): Promise<T> {
  const { token, ...fetchOptions } = options;

  let accessToken = token;
  if (!accessToken) {
    try {
      const stored = localStorage.getItem("auth-storage");
      if (stored) {
        const { state } = JSON.parse(stored);
        accessToken = state?.tokens?.access_token;
      }
    } catch {
      // ignore
    }
  }

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(fetchOptions.headers as Record<string, string>),
  };

  if (accessToken) {
    headers["Authorization"] = `Bearer ${accessToken}`;
  }

  let res = await fetch(`${API_URL}${path}`, {
    ...fetchOptions,
    headers,
  });

  if (res.status === 401 && accessToken && !path.includes("/auth/")) {
    if (!isRefreshing) {
      isRefreshing = true;
      refreshPromise = refreshAccessToken();
    }
    const newToken = await refreshPromise;
    isRefreshing = false;
    refreshPromise = null;

    if (newToken) {
      headers["Authorization"] = `Bearer ${newToken}`;
      res = await fetch(`${API_URL}${path}`, { ...fetchOptions, headers });
    }

    if (res.status === 401) {
      localStorage.removeItem("auth-storage");
      window.location.href = "/login";
      throw new Error("Sesión expirada");
    }
  }

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: "Error desconocido" }));
    throw new Error(error.detail || `HTTP ${res.status}`);
  }

  if (res.status === 204) return undefined as T;

  return res.json();
}
