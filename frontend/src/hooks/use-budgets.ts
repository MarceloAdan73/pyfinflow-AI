"use client";

import useSWR from "swr";
import { api } from "@/lib/api";
import type { Budget, BudgetCreate } from "@/types";

const fetcher = (url: string) => api<Budget[]>(url);

export function useBudgets(mes: string) {
  const url = `/budgets?mes=${mes}`;
  const { data, error, isLoading, mutate } = useSWR(mes ? url : null, fetcher);

  const createBudget = async (budget: BudgetCreate) => {
    const created = await api<Budget>("/budgets", {
      method: "POST",
      body: JSON.stringify(budget),
    });
    mutate();
    return created;
  };

  return {
    budgets: data || [],
    isLoading,
    error,
    mutate,
    createBudget,
  };
}
