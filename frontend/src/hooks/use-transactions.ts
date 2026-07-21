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

  return {
    transactions: data || [],
    isLoading,
    error,
    mutate,
    createTransaction,
    updateTransaction,
    deleteTransaction,
  };
}
