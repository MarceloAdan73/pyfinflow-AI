"use client";

import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { formatMoney, formatDate, type CurrencyCode } from "@/lib/utils";
import type { Transaction } from "@/types";
import { ArrowRight } from "lucide-react";
import { useLocale, useTranslations } from "next-intl";

interface Props {
  transactions: Transaction[];
  isLoading: boolean;
  currency: CurrencyCode;
}

export function RecentTransactions({ transactions, isLoading, currency }: Props) {
  const t = useTranslations("dashboard");
  const locale = useLocale();

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <Skeleton className="h-5 w-40" />
        </CardHeader>
        <CardContent className="space-y-3">
          {[1, 2, 3, 4, 5].map((i) => (
            <Skeleton key={i} className="h-14 w-full rounded-lg" />
          ))}
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle className="text-base">{t("recentTransactions")}</CardTitle>
        <Link href={`/${locale}/transactions`}>
          <Button variant="ghost" size="sm" className="gap-1 text-xs">
            {t("viewAll")} <ArrowRight className="h-3 w-3" />
          </Button>
        </Link>
      </CardHeader>
      <CardContent>
        {transactions.length === 0 ? (
          <p className="text-muted-foreground text-sm text-center py-4">
            {t("noTransactions")}
          </p>
        ) : (
          <div className="space-y-2">
            {transactions.map((txn) => (
              <div
                key={txn.id}
                className="flex items-center justify-between p-3 rounded-lg bg-secondary/50 hover:bg-secondary transition-colors"
              >
                <div className="flex items-center gap-3">
                  <div
                    className={`h-8 w-8 rounded-full flex items-center justify-center text-xs font-bold ${
                      txn.tipo === "Ingreso"
                        ? "bg-emerald-500/20 text-emerald-400"
                        : "bg-red-500/20 text-red-400"
                    }`}
                  >
                    {txn.tipo === "Ingreso" ? "+" : "-"}
                  </div>
                  <div>
                    <p className="text-sm font-medium">{txn.descripcion || txn.categoria}</p>
                    <p className="text-xs text-muted-foreground">
                      {txn.categoria} · {formatDate(txn.fecha)}
                    </p>
                  </div>
                </div>
                <span
                  className={`text-sm font-semibold ${
                    txn.tipo === "Ingreso" ? "text-emerald-400" : "text-red-400"
                  }`}
                >
                  {txn.tipo === "Ingreso" ? "+" : "-"}
                  {formatMoney(txn.monto, currency)}
                </span>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
