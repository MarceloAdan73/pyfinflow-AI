"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { useTranslations } from "next-intl";
import { formatMoney, type CurrencyCode } from "@/lib/utils";

interface MonthlyData {
  month: string;
  ingresos: number;
  gastos: number;
}

interface Props {
  data: MonthlyData[];
  isLoading: boolean;
  currency: CurrencyCode;
}

export function MonthlyChart({ data, isLoading, currency }: Props) {
  const t = useTranslations("dashboard");

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <Skeleton className="h-5 w-40" />
        </CardHeader>
        <CardContent>
          <Skeleton className="h-[300px] w-full rounded-lg" />
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">{t("incomeVsExpenses")}</CardTitle>
      </CardHeader>
      <CardContent>
        {data.length === 0 ? (
          <div className="h-[300px] flex items-center justify-center text-muted-foreground text-sm">
            {t("noData")}
          </div>
        ) : (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={data}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
              <XAxis dataKey="month" stroke="var(--muted-foreground)" fontSize={12} tickLine={false} />
              <YAxis stroke="var(--muted-foreground)" fontSize={12} tickLine={false} axisLine={false} />
              <Tooltip
                formatter={(value) => {
                  const v = Array.isArray(value) ? value[0] : value;
                  return formatMoney(Number(v ?? 0), currency);
                }}
                cursor={{ fill: "var(--muted)", opacity: 0.5 }}
                contentStyle={{
                  backgroundColor: "var(--card)",
                  border: "1px solid var(--border)",
                  borderRadius: "8px",
                  color: "var(--foreground)",
                }}
              />
              <Legend />
              <Bar dataKey="ingresos" name={t("income")} fill="#2dd4bf" radius={[4, 4, 0, 0]} opacity={0.85} />
              <Bar dataKey="gastos" name={t("expenses")} fill="#f472b6" radius={[4, 4, 0, 0]} opacity={0.85} />
            </BarChart>
          </ResponsiveContainer>
        )}
      </CardContent>
    </Card>
  );
}
