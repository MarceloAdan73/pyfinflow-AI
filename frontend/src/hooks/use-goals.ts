"use client";

import useSWR from "swr";
import { api } from "@/lib/api";
import type { Goal, GoalCreate, GoalUpdate } from "@/types";

const fetcher = (url: string) => api<Goal[]>(url);

export function useGoals() {
  const { data, error, isLoading, mutate } = useSWR("/goals", fetcher);

  const createGoal = async (goal: GoalCreate) => {
    const created = await api<Goal>("/goals", {
      method: "POST",
      body: JSON.stringify(goal),
    });
    mutate();
    return created;
  };

  const updateGoal = async (id: string, goal: GoalUpdate) => {
    const updated = await api<Goal>(`/goals/${id}`, {
      method: "PUT",
      body: JSON.stringify(goal),
    });
    mutate();
    return updated;
  };

  const deleteGoal = async (id: string) => {
    await api(`/goals/${id}`, { method: "DELETE" });
    mutate();
  };

  return {
    goals: data || [],
    isLoading,
    error,
    mutate,
    createGoal,
    updateGoal,
    deleteGoal,
  };
}
