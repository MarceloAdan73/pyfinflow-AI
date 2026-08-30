"use client";

import { useMemo, useState } from "react";
import { DashboardLayout } from "@/components/layout/dashboard-layout";
import { SummaryCards } from "@/components/dashboard/summary-cards";
import { MonthlyChart } from "@/components/dashboard/monthly-chart";
import { CategoryPie } from "@/components/dashboard/category-pie";
import { RecentTransactions } from "@/components/dashboard/recent-transactions";
import { useTransactions } from "@/hooks/use-transactions";
import { useBudgetAlerts } from "@/hooks/use-budget-alerts";
import { useCurrency } from "@/lib/use-currency";
import { PageTransition, StaggerContainer, StaggerItem } from "@/components/ui/motion";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Calendar, AlertTriangle } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useTranslations } from "next-intl";
import { getCurrentMonth, formatMoney } from "@/lib/utils";

export default function DashboardPage() {
  const t = useTranslations("dashboard");
  const tc = useTranslations("common");
  const { transactions, isLoading } = useTransactions();
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const [displayCurrency] = useCurrency();
  const currentMonth = getCurrentMonth();
  const { alerts: budgetAlerts } = useBudgetAlerts(currentMonth);

  const filteredTransactions = useMemo(() => {
    return transactions.filter((tx) => {
      if (dateFrom && tx.fecha < dateFrom) return false;
      if (dateTo && tx.fecha > dateTo) return false;
      return true;
    });
  }, [transactions, dateFrom, dateTo]);

  const summary = useMemo(() => {
    const ingresos = filteredTransactions
      .filter((tx) => tx.tipo === "Ingreso")
      .reduce((sum, tx) => sum + tx.monto, 0);
    const gastos = filteredTransactions
      .filter((tx) => tx.tipo === "Gasto")
      .reduce((sum, tx) => sum + tx.monto, 0);
    const balance = ingresos - gastos;
    return { ingresos, gastos, balance };
  }, [filteredTransactions]);

  const categoryData = useMemo(() => {
    const gastos = filteredTransactions.filter((tx) => tx.tipo === "Gasto");
    const byCategory: Record<string, number> = {};
    gastos.forEach((tx) => {
      byCategory[tx.categoria] = (byCategory[tx.categoria] || 0) + tx.monto;
    });
    return Object.entries(byCategory)
      .map(([name, value]) => ({ name, value }))
      .sort((a, b) => b.value - a.value);
  }, [filteredTransactions]);

  const monthlyData = useMemo(() => {
    const byMonth: Record<string, { ingresos: number; gastos: number }> = {};
    filteredTransactions.forEach((tx) => {
      const month = tx.fecha.substring(0, 7);
      if (!byMonth[month]) byMonth[month] = { ingresos: 0, gastos: 0 };
      if (tx.tipo === "Ingreso") byMonth[month].ingresos += tx.monto;
      else byMonth[month].gastos += tx.monto;
    });
    return Object.entries(byMonth)
      .sort(([a], [b]) => a.localeCompare(b))
      .slice(-6)
      .map(([month, data]) => ({ month, ...data }));
  }, [filteredTransactions]);

  const clearDates = () => {
    setDateFrom("");
    setDateTo("");
  };

  return (
    <DashboardLayout>
      <PageTransition>
        <StaggerContainer className="space-y-6">
          <StaggerItem>
            <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
              <div>
                <h1 className="text-2xl font-bold">{t("title")}</h1>
                <p className="text-muted-foreground">{t("description")}</p>
              </div>
              <div className="flex items-center gap-2">
                <Calendar className="h-4 w-4 text-muted-foreground shrink-0" />
                <div className="flex items-end gap-2">
                  <div className="space-y-1">
                    <Label className="block text-xs text-muted-foreground">{t("from")}</Label>
                    <Input
                      type="date"
                      value={dateFrom}
                      onChange={(e) => setDateFrom(e.target.value)}
                      className="w-36 text-xs"
                    />
                  </div>
                  <div className="space-y-1">
                    <Label className="block text-xs text-muted-foreground">{t("to")}</Label>
                    <Input
                      type="date"
                      value={dateTo}
                      onChange={(e) => setDateTo(e.target.value)}
                      className="w-36 text-xs"
                    />
                  </div>
                  {(dateFrom || dateTo) && (
                    <Button variant="ghost" size="sm" onClick={clearDates}>
                      {tc("clear")}
                    </Button>
                  )}
                </div>
              </div>
            </div>
          </StaggerItem>

          {budgetAlerts.length > 0 && (
            <StaggerItem>
              <Card className="border-amber-200 bg-amber-50 dark:border-amber-900 dark:bg-amber-950/30">
                <CardContent className="pt-4 pb-4">
                  <div className="flex items-center gap-2 mb-2">
                    <AlertTriangle className="h-4 w-4 text-amber-600" />
                    <span className="font-semibold text-sm">
                      {budgetAlerts.length} {budgetAlerts.length === 1 ? "alerta" : "alertas"} de presupuesto — {currentMonth}
                    </span>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {budgetAlerts.map((a) => (
                      <Badge
                        key={a.categoria}
                        variant={a.excedido ? "destructive" : "secondary"}
                        className={a.excedido ? "" : "bg-amber-500 text-white hover:bg-amber-600"}
                      >
                        {a.categoria}: {a.porcentaje.toFixed(0)}% ({formatMoney(a.gastado)}/{formatMoney(a.limite)})
                      </Badge>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </StaggerItem>
          )}

          <StaggerItem>
            <SummaryCards
              summary={summary}
              isLoading={isLoading}
              transactions={filteredTransactions}
              currency={displayCurrency}
            />
          </StaggerItem>

          <StaggerItem>
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2">
                <MonthlyChart data={monthlyData} isLoading={isLoading} currency={displayCurrency} />
              </div>
              <div>
                <CategoryPie data={categoryData} isLoading={isLoading} currency={displayCurrency} />
              </div>
            </div>
          </StaggerItem>

          <StaggerItem>
            <RecentTransactions transactions={filteredTransactions.slice(0, 5)} isLoading={isLoading} currency={displayCurrency} />
          </StaggerItem>
        </StaggerContainer>
      </PageTransition>
    </DashboardLayout>
  );
}
