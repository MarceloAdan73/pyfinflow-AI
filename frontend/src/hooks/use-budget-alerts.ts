"use client";

import useSWR from "swr";
import { api } from "@/lib/api";
import type { BudgetAlert } from "@/types";

const fetcher = (url: string) => api<BudgetAlert[]>(url);

export function useBudgetAlerts(mes: string) {
  const url = mes ? `/budgets/alerts?mes=${mes}` : null;
  const { data, error, isLoading, mutate } = useSWR(url, fetcher);

  return {
    alerts: data || [],
    isLoading,
    error,
    mutate,
  };
}
