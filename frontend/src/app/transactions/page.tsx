"use client";

import { useState } from "react";
import { DashboardLayout } from "@/components/layout/dashboard-layout";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Select } from "@/components/ui/select";
import { useTransactions } from "@/hooks/use-transactions";
import { formatMoney, formatDate } from "@/lib/utils";
import type { TransactionCreate } from "@/types";
import { Plus, Trash2, Edit, Filter } from "lucide-react";
import { PageTransition, StaggerContainer, StaggerItem } from "@/components/ui/motion";

const categorias = [
  "Alimentación", "Transporte", "Servicios", "Ocio", "Salud",
  "Educación", "Ropa", "Hogar", "Salary", "Freelance", "Inversiones", "Otros",
];

export default function TransactionsPage() {
  const [filters, setFilters] = useState<Record<string, string>>({});
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const { transactions, isLoading, createTransaction, updateTransaction, deleteTransaction } = useTransactions(filters);

  const [form, setForm] = useState<TransactionCreate>({
    tipo: "Gasto",
    monto: 0,
    categoria: "Alimentación",
    descripcion: "",
    fecha: new Date().toISOString().split("T")[0],
    moneda: "ARS",
  });

  const openCreate = () => {
    setEditingId(null);
    setForm({
      tipo: "Gasto",
      monto: 0,
      categoria: "Alimentación",
      descripcion: "",
      fecha: new Date().toISOString().split("T")[0],
      moneda: "ARS",
    });
    setDialogOpen(true);
  };

  const openEdit = (txn: typeof transactions[0]) => {
    setEditingId(txn.id);
    setForm({
      tipo: txn.tipo as "Ingreso" | "Gasto",
      monto: txn.monto,
      categoria: txn.categoria,
      descripcion: txn.descripcion,
      fecha: txn.fecha,
      moneda: txn.moneda,
    });
    setDialogOpen(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (editingId) {
      await updateTransaction(editingId, form);
    } else {
      await createTransaction(form);
    }
    setDialogOpen(false);
  };

  const handleDelete = async (id: string) => {
    if (confirm("¿Eliminar esta transacción?")) {
      await deleteTransaction(id);
    }
  };

  return (
    <DashboardLayout>
      <PageTransition>
        <StaggerContainer className="space-y-6">
          <StaggerItem>
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-2xl font-bold">Transacciones</h1>
                <p className="text-muted-foreground">Gestioná tus ingresos y gastos</p>
              </div>
              <Button onClick={openCreate} className="gap-2">
                <Plus className="h-4 w-4" /> Nueva
              </Button>
            </div>
          </StaggerItem>

          <StaggerItem>
            <Card>
              <CardHeader>
                <div className="flex items-center gap-2">
                  <Filter className="h-4 w-4 text-muted-foreground" />
                  <Select
                    value={filters.tipo || ""}
                    onChange={(e) => setFilters((f) => ({ ...f, tipo: e.target.value }))}
                    className="w-40"
                  >
                    <option value="">Todos</option>
                    <option value="Ingreso">Ingresos</option>
                    <option value="Gasto">Gastos</option>
                  </Select>
                  <Select
                    value={filters.categoria || ""}
                    onChange={(e) => setFilters((f) => ({ ...f, categoria: e.target.value }))}
                    className="w-48"
                  >
                    <option value="">Todas las categorías</option>
                    {categorias.map((c) => (
                      <option key={c} value={c}>{c}</option>
                    ))}
                  </Select>
                </div>
              </CardHeader>
              <CardContent>
                {isLoading ? (
                  <div className="space-y-3">
                    {[1, 2, 3, 4, 5].map((i) => (
                      <Skeleton key={i} className="h-14 w-full rounded-lg" />
                    ))}
                  </div>
                ) : transactions.length === 0 ? (
                  <p className="text-center text-muted-foreground py-8">No hay transacciones</p>
                ) : (
                  <div className="space-y-2">
                    {transactions.map((txn) => (
                      <div
                        key={txn.id}
                        className="flex items-center justify-between p-3 rounded-lg bg-secondary/50 hover:bg-secondary transition-colors group"
                      >
                        <div className="flex items-center gap-3">
                          <div
                            className={`h-9 w-9 rounded-full flex items-center justify-center text-xs font-bold ${
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
                        <div className="flex items-center gap-3">
                          <span
                            className={`text-sm font-semibold ${
                              txn.tipo === "Ingreso" ? "text-emerald-400" : "text-red-400"
                            }`}
                          >
                            {txn.tipo === "Ingreso" ? "+" : "-"}{formatMoney(txn.monto)}
                          </span>
                          <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                            <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => openEdit(txn)}>
                              <Edit className="h-3 w-3" />
                            </Button>
                            <Button variant="ghost" size="icon" className="h-7 w-7 text-destructive" onClick={() => handleDelete(txn.id)}>
                              <Trash2 className="h-3 w-3" />
                            </Button>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </StaggerItem>
        </StaggerContainer>
      </PageTransition>

      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{editingId ? "Editar" : "Nueva"} Transacción</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Tipo</Label>
                <Select
                  value={form.tipo}
                  onChange={(e) => setForm((f) => ({ ...f, tipo: e.target.value as "Ingreso" | "Gasto" }))}
                >
                  <option value="Ingreso">Ingreso</option>
                  <option value="Gasto">Gasto</option>
                </Select>
              </div>
              <div className="space-y-2">
                <Label>Monto</Label>
                <Input
                  type="number"
                  step="0.01"
                  min="0"
                  value={form.monto || ""}
                  onChange={(e) => setForm((f) => ({ ...f, monto: parseFloat(e.target.value) || 0 }))}
                  required
                />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
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
                <Label>Fecha</Label>
                <Input
                  type="date"
                  value={form.fecha}
                  onChange={(e) => setForm((f) => ({ ...f, fecha: e.target.value }))}
                  required
                />
              </div>
            </div>
            <div className="space-y-2">
              <Label>Descripción (opcional)</Label>
              <Input
                value={form.descripcion}
                onChange={(e) => setForm((f) => ({ ...f, descripcion: e.target.value }))}
                placeholder="Descripción breve"
              />
            </div>
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setDialogOpen(false)}>Cancelar</Button>
              <Button type="submit">{editingId ? "Actualizar" : "Crear"}</Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </DashboardLayout>
  );
}
