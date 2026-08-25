"use client";

import useSWR from "swr";
import { api } from "@/lib/api";
import type { Transaction, TransactionCreate } from "@/types";

const fetcher = (url: string) => api<Transaction[]>(url);

export function useTransactions(filters?: Record<string, string>) {
  const params = new URLSearchParams();
  if (filters) {
    Object.entries(filters).forEach(([k, v]) => {
      if (v) params.set(k, v);
    });
  }
  const qs = params.toString();
  const url = `/transactions${qs ? `?${qs}` : ""}`;

  const { data, error, isLoading, mutate } = useSWR(url, fetcher);

  const createTransaction = async (txn: TransactionCreate) => {
    const created = await api<Transaction>("/transactions", {
      method: "POST",
      body: JSON.stringify(txn),
    });
    mutate();
    return created;
  };

  const updateTransaction = async (id: string, txn: Partial<TransactionCreate>) => {
    const updated = await api<Transaction>(`/transactions/${id}`, {
      method: "PUT",
      body: JSON.stringify(txn),
    });
    mutate();
    return updated;
  };

  const deleteTransaction = async (id: string) => {
    await api(`/transactions/${id}`, { method: "DELETE" });
    mutate();
  };

  const importTransactions = async (file: File) => {
    const form = new FormData();
    form.append("file", file);
    // api() fuerza Content-Type json; para FormData usamos fetch directo con token
    const stored = typeof window !== "undefined" ? localStorage.getItem("auth-storage") : null;
    let token: string | undefined;
    try {
      if (stored) token = JSON.parse(stored)?.state?.tokens?.access_token;
    } catch {}
    const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    const headers: Record<string, string> = {};
    if (token) headers["Authorization"] = `Bearer ${token}`;
    const res = await fetch(`${API_URL}/transactions/import`, {
      method: "POST",
      headers,
      body: form,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Error importando CSV" }));
      throw new Error(err.detail || `HTTP ${res.status}`);
    }
    const data = await res.json();
    mutate();
    return data as { imported: number; skipped: number; errors: { row: number; detail: string }[]; total_rows: number };
  };

  return {
    transactions: data || [],
    isLoading,
    error,
    mutate,
    createTransaction,
    updateTransaction,
    deleteTransaction,
    importTransactions,
  };
}
