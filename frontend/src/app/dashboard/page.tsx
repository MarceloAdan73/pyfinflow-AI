"use client";

import { useMemo } from "react";
import { DashboardLayout } from "@/components/layout/dashboard-layout";
import { SummaryCards } from "@/components/dashboard/summary-cards";
import { MonthlyChart } from "@/components/dashboard/monthly-chart";
import { CategoryPie } from "@/components/dashboard/category-pie";
import { RecentTransactions } from "@/components/dashboard/recent-transactions";
import { useTransactions } from "@/hooks/use-transactions";
import { PageTransition, StaggerContainer, StaggerItem } from "@/components/ui/motion";

export default function DashboardPage() {
  const { transactions, isLoading } = useTransactions();

  const summary = useMemo(() => {
    const ingresos = transactions
      .filter((t) => t.tipo === "Ingreso")
      .reduce((sum, t) => sum + t.monto, 0);
    const gastos = transactions
      .filter((t) => t.tipo === "Gasto")
      .reduce((sum, t) => sum + t.monto, 0);
    const balance = ingresos - gastos;
    return { ingresos, gastos, balance };
  }, [transactions]);

  const categoryData = useMemo(() => {
    const gastos = transactions.filter((t) => t.tipo === "Gasto");
    const byCategory: Record<string, number> = {};
    gastos.forEach((t) => {
      byCategory[t.categoria] = (byCategory[t.categoria] || 0) + t.monto;
    });
    return Object.entries(byCategory)
      .map(([name, value]) => ({ name, value }))
      .sort((a, b) => b.value - a.value);
  }, [transactions]);

  const monthlyData = useMemo(() => {
    const byMonth: Record<string, { ingresos: number; gastos: number }> = {};
    transactions.forEach((t) => {
      const month = t.fecha.substring(0, 7);
      if (!byMonth[month]) byMonth[month] = { ingresos: 0, gastos: 0 };
      if (t.tipo === "Ingreso") byMonth[month].ingresos += t.monto;
      else byMonth[month].gastos += t.monto;
    });
    return Object.entries(byMonth)
      .sort(([a], [b]) => a.localeCompare(b))
      .slice(-6)
      .map(([month, data]) => ({ month, ...data }));
  }, [transactions]);

  return (
    <DashboardLayout>
      <PageTransition>
        <StaggerContainer className="space-y-6">
          <StaggerItem>
            <div>
              <h1 className="text-2xl font-bold">Dashboard</h1>
              <p className="text-muted-foreground">Resumen financiero de tu cuenta</p>
            </div>
          </StaggerItem>

          <StaggerItem>
            <SummaryCards summary={summary} isLoading={isLoading} />
          </StaggerItem>

          <StaggerItem>
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2">
                <MonthlyChart data={monthlyData} isLoading={isLoading} />
              </div>
              <div>
                <CategoryPie data={categoryData} isLoading={isLoading} />
              </div>
            </div>
          </StaggerItem>

          <StaggerItem>
            <RecentTransactions transactions={transactions.slice(0, 5)} isLoading={isLoading} />
          </StaggerItem>
        </StaggerContainer>
      </PageTransition>
    </DashboardLayout>
  );
}
