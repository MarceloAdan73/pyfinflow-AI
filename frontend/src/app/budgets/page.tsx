"use client";

import { useState } from "react";
import { DashboardLayout } from "@/components/layout/dashboard-layout";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Select } from "@/components/ui/select";
import { useBudgets } from "@/hooks/use-budgets";
import { useTransactions } from "@/hooks/use-transactions";
import { formatMoney, getCurrentMonth } from "@/lib/utils";
import type { BudgetCreate } from "@/types";
import { Plus, AlertTriangle } from "lucide-react";
import { useMemo } from "react";
import { PageTransition, StaggerContainer, StaggerItem } from "@/components/ui/motion";

const categorias = [
  "Alimentación", "Transporte", "Servicios", "Ocio", "Salud",
  "Educación", "Ropa", "Hogar", "Otros",
];

export default function BudgetsPage() {
  const currentMonth = getCurrentMonth();
  const [mes, setMes] = useState(currentMonth);
  const [dialogOpen, setDialogOpen] = useState(false);
  const { budgets, isLoading: budgetsLoading, createBudget } = useBudgets(mes);
  const { transactions, isLoading: txnsLoading } = useTransactions({ fecha_inicio: `${mes}-01`, fecha_fin: `${mes}-31` });

  const [form, setForm] = useState<BudgetCreate>({
    categoria: "Alimentación",
    limite: 0,
    mes: currentMonth,
  });

  const isLoading = budgetsLoading || txnsLoading;

  const budgetsWithSpent = useMemo(() => {
    const gastosByCategory: Record<string, number> = {};
    transactions
      .filter((t) => t.tipo === "Gasto")
      .forEach((t) => {
        gastosByCategory[t.categoria] = (gastosByCategory[t.categoria] || 0) + t.monto;
      });

    return budgets.map((b) => {
      const gastado = gastosByCategory[b.categoria] || 0;
      const porcentaje = b.limite > 0 ? (gastado / b.limite) * 100 : 0;
      return { ...b, gastado, porcentaje, excedido: gastado > b.limite };
    });
  }, [budgets, transactions]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await createBudget({ ...form, mes });
    setDialogOpen(false);
  };

  return (
    <DashboardLayout>
      <PageTransition>
        <StaggerContainer className="space-y-6">
          <StaggerItem>
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-2xl font-bold">Presupuestos</h1>
                <p className="text-muted-foreground">Controlá tus gastos por categoría</p>
              </div>
              <div className="flex items-center gap-3">
                <Input
                  type="month"
                  value={mes}
                  onChange={(e) => setMes(e.target.value)}
                  className="w-44"
                />
                <Button onClick={() => { setForm((f) => ({ ...f, mes })); setDialogOpen(true); }} className="gap-2">
                  <Plus className="h-4 w-4" /> Nuevo
                </Button>
              </div>
            </div>
          </StaggerItem>

          <StaggerItem>
            {isLoading ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {[1, 2, 3].map((i) => (
                  <Card key={i}>
                    <CardContent className="pt-6 space-y-3">
                      <Skeleton className="h-5 w-32" />
                      <Skeleton className="h-4 w-full" />
                      <Skeleton className="h-6 w-24" />
                    </CardContent>
                  </Card>
                ))}
              </div>
            ) : budgetsWithSpent.length === 0 ? (
              <Card>
                <CardContent className="py-12 text-center text-muted-foreground">
                  No hay presupuestos para {mes}
                </CardContent>
              </Card>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {budgetsWithSpent.map((b) => (
                  <Card key={b.id}>
                    <CardContent className="pt-6 space-y-3">
                      <div className="flex items-center justify-between">
                        <h3 className="font-semibold">{b.categoria}</h3>
                        {b.excedido && (
                          <Badge variant="destructive" className="gap-1">
                            <AlertTriangle className="h-3 w-3" /> Excedido
                          </Badge>
                        )}
                      </div>
                      <Progress
                        value={Math.min(b.porcentaje, 100)}
                        indicatorClassName={b.excedido ? "bg-destructive" : b.porcentaje > 80 ? "bg-amber-500" : "bg-primary"}
                      />
                      <div className="flex justify-between text-sm">
                        <span className="text-muted-foreground">
                          {formatMoney(b.gastado)} / {formatMoney(b.limite)}
                        </span>
                        <span className={`font-medium ${b.excedido ? "text-destructive" : "text-muted-foreground"}`}>
                          {b.porcentaje.toFixed(0)}%
                        </span>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </StaggerItem>
        </StaggerContainer>
      </PageTransition>

      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Nuevo Presupuesto</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label>Categoría</Label>
              <Select
                value={form.categoria}
                onChange={(e) => setForm((f) => ({ ...f, categoria: e.target.value }))}
              >
                {categorias.map((c) => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </Select>
            </div>
            <div className="space-y-2">
              <Label>Límite mensual</Label>
              <Input
                type="number"
                step="0.01"
                min="0"
                value={form.limite || ""}
                onChange={(e) => setForm((f) => ({ ...f, limite: parseFloat(e.target.value) || 0 }))}
                required
              />
            </div>
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setDialogOpen(false)}>Cancelar</Button>
              <Button type="submit">Crear</Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </DashboardLayout>
  );
}
