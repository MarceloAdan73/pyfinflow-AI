"use client";

import { useMemo } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { TrendingUp, TrendingDown, Wallet, ArrowUp, ArrowDown, Minus } from "lucide-react";
import { useTranslations } from "next-intl";
import { useFormatMoney } from "@/lib/use-money";

interface SummaryProps {
  summary: { ingresos: number; gastos: number; balance: number };
  isLoading: boolean;
  transactions?: { tipo: string; monto: number; fecha: string; moneda?: string }[];
  currency?: string;
}

export function SummaryCards({ summary, isLoading, transactions = [] }: SummaryProps) {
  const t = useTranslations("dashboard");
  const formatMoney = useFormatMoney();
  const trends = useMemo(() => {
    const now = new Date();
    const currentMonth = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}`;
    const prevDate = new Date(now.getFullYear(), now.getMonth() - 1, 1);
    const prevMonth = `${prevDate.getFullYear()}-${String(prevDate.getMonth() + 1).padStart(2, "0")}`;

    const calcTrend = (tipo: string) => {
      const current = transactions
        .filter((t) => t.tipo === tipo && t.fecha.startsWith(currentMonth))
        .reduce((sum, t) => sum + t.monto, 0);
      const prev = transactions
        .filter((t) => t.tipo === tipo && t.fecha.startsWith(prevMonth))
        .reduce((sum, t) => sum + t.monto, 0);

      if (prev === 0 && current === 0) return { direction: "stable" as const, pct: 0 };
      if (prev === 0) return { direction: "up" as const, pct: 100 };
      const pct = ((current - prev) / prev) * 100;
      if (Math.abs(pct) < 1) return { direction: "stable" as const, pct: 0 };
      return { direction: pct > 0 ? ("up" as const) : ("down" as const), pct: Math.abs(Math.round(pct)) };
    };

    return {
      ingresos: calcTrend("Ingreso"),
      gastos: calcTrend("Gasto"),
    };
  }, [transactions]);

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {[1, 2, 3].map((i) => (
          <Card key={i}>
            <Skeleton className="h-4 w-24 mb-3" />
            <Skeleton className="h-8 w-32" />
          </Card>
        ))}
      </div>
    );
  }

  const TrendIcon = ({ direction }: { direction: "up" | "down" | "stable"; pct: number }) => {
    if (direction === "stable") return <Minus className="h-3 w-3 text-muted-foreground" />;
    if (direction === "up") return <ArrowUp className="h-3 w-3 text-emerald-400" />;
    return <ArrowDown className="h-3 w-3 text-red-400" />;
  };

  const TrendBadge = ({ direction, pct }: { direction: "up" | "down" | "stable"; pct: number }) => {
    if (direction === "stable" && pct === 0) return null;
    return (
      <span className={`text-xs font-medium ${
        direction === "up" ? "text-emerald-400" : direction === "down" ? "text-red-400" : "text-muted-foreground"
      }`}>
        <TrendIcon direction={direction} pct={pct} /> {pct}%
      </span>
    );
  };

  const cards = [
    {
      title: t("income"),
      value: summary.ingresos,
      icon: TrendingUp,
      color: "text-emerald-400",
      bgColor: "bg-emerald-500/10",
      trend: trends.ingresos,
    },
    {
      title: t("expenses"),
      value: summary.gastos,
      icon: TrendingDown,
      color: "text-red-400",
      bgColor: "bg-red-500/10",
      trend: trends.gastos,
    },
    {
      title: t("balance"),
      value: summary.balance,
      icon: Wallet,
      color: summary.balance >= 0 ? "text-emerald-400" : "text-red-400",
      bgColor: summary.balance >= 0 ? "bg-emerald-500/10" : "bg-red-500/10",
      trend: null,
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
      {cards.map((card) => (
        <Card key={card.title}>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">{card.title}</CardTitle>
            <div className={`h-8 w-8 rounded-lg ${card.bgColor} flex items-center justify-center`}>
              <card.icon className={`h-4 w-4 ${card.color}`} />
            </div>
          </CardHeader>
          <CardContent>
            <div className="flex items-end gap-2">
              <div className={`text-2xl font-bold ${card.color}`}>
                {formatMoney(card.value)}
              </div>
              {card.trend && (
                <div className="flex items-center gap-1 mb-1">
                  <TrendBadge direction={card.trend.direction} pct={card.trend.pct} />
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
