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
import { useGoals } from "@/hooks/use-goals";
import { formatMoney, formatDate } from "@/lib/utils";
import type { GoalCreate } from "@/types";
import { Plus, Trash2, Target, Edit } from "lucide-react";
import { PageTransition, StaggerContainer, StaggerItem } from "@/components/ui/motion";
import { ConfirmDialog } from "@/components/ui/confirm-dialog";

export default function GoalsPage() {
  const [dialogOpen, setDialogOpen] = useState(false);
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [deleteTargetId, setDeleteTargetId] = useState<string | null>(null);
  const [editingId, setEditingId] = useState<string | null>(null);
  const { goals, isLoading, createGoal, updateGoal, deleteGoal } = useGoals();

  const [form, setForm] = useState<GoalCreate>({
    nombre: "",
    objetivo: 0,
    fecha_limite: null,
    categoria: null,
  });

  const openCreate = () => {
    setEditingId(null);
    setForm({ nombre: "", objetivo: 0, fecha_limite: null, categoria: null });
    setDialogOpen(true);
  };

  const openEdit = (goal: typeof goals[0]) => {
    setEditingId(goal.id);
    setForm({
      nombre: goal.nombre,
      objetivo: goal.objetivo,
      fecha_limite: goal.fecha_limite,
      categoria: goal.categoria,
    });
    setDialogOpen(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (editingId) {
      await updateGoal(editingId, form);
    } else {
      await createGoal(form);
    }
    setDialogOpen(false);
  };

  return (
    <DashboardLayout>
      <PageTransition>
        <StaggerContainer className="space-y-6">
          <StaggerItem>
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-2xl font-bold">Metas de Ahorro</h1>
                <p className="text-muted-foreground">Definí y seguí tus objetivos financieros</p>
              </div>
              <Button onClick={openCreate} className="gap-2">
                <Plus className="h-4 w-4" /> Nueva Meta
              </Button>
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
            ) : goals.length === 0 ? (
              <Card>
                <CardContent className="py-12 text-center text-muted-foreground">
                  <Target className="h-12 w-12 mx-auto mb-3 opacity-30" />
                  No tenés metas creadas. ¡Creá una!
                </CardContent>
              </Card>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {goals.map((goal) => {
                  const pct = goal.objetivo > 0 ? (goal.ahorrado / goal.objetivo) * 100 : 0;
                  const completed = pct >= 100;
                  return (
                    <Card key={goal.id} className="relative group">
                      <CardContent className="pt-6 space-y-3">
                        <div className="flex items-center justify-between">
                          <h3 className="font-semibold">{goal.nombre}</h3>
                          <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                            <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => openEdit(goal)}>
                              <Edit className="h-3 w-3" />
                            </Button>
                            <Button variant="ghost" size="icon" className="h-7 w-7 text-destructive" onClick={() => {
                              setDeleteTargetId(goal.id);
                              setConfirmOpen(true);
                            }}>
                              <Trash2 className="h-3 w-3" />
                            </Button>
                          </div>
                        </div>
                        {goal.categoria && <Badge variant="secondary">{goal.categoria}</Badge>}
                        <Progress
                          value={Math.min(pct, 100)}
                          indicatorClassName={completed ? "bg-emerald-500" : "bg-primary"}
                        />
                        <div className="flex justify-between text-sm">
                          <span className="text-muted-foreground">
                            {formatMoney(goal.ahorrado)} / {formatMoney(goal.objetivo)}
                          </span>
                          <span className={`font-medium ${completed ? "text-emerald-400" : "text-muted-foreground"}`}>
                            {pct.toFixed(0)}%
                          </span>
                        </div>
                        {goal.fecha_limite && (
                          <p className="text-xs text-muted-foreground">
                            Fecha límite: {formatDate(goal.fecha_limite)}
                          </p>
                        )}
                        {!completed && (
                          <div className="pt-2">
                            <div className="flex gap-2">
                              <Input
                                type="number"
                                placeholder="Agregar..."
                                className="h-8 text-xs"
                                id={`add-${goal.id}`}
                              />
                              <Button
                                size="sm"
                                variant="outline"
                                className="h-8 text-xs"
                                onClick={async () => {
                                  const input = document.getElementById(`add-${goal.id}`) as HTMLInputElement;
                                  const amount = parseFloat(input.value);
                                  if (amount > 0) {
                                    await updateGoal(goal.id, { ahorrado: goal.ahorrado + amount });
                                    input.value = "";
                                  }
                                }}
                              >
                                + Ahorrar
                              </Button>
                            </div>
                          </div>
                        )}
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
            )}
          </StaggerItem>
        </StaggerContainer>
      </PageTransition>

      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{editingId ? "Editar" : "Nueva"} Meta</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label>Nombre</Label>
              <Input
                value={form.nombre}
                onChange={(e) => setForm((f) => ({ ...f, nombre: e.target.value }))}
                placeholder="Ej: Viaje a Europa"
                required
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Objetivo ($)</Label>
                <Input
                  type="number"
                  step="0.01"
                  min="0"
                  value={form.objetivo || ""}
                  onChange={(e) => setForm((f) => ({ ...f, objetivo: parseFloat(e.target.value) || 0 }))}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label>Fecha límite</Label>
                <Input
                  type="date"
                  value={form.fecha_limite || ""}
                  onChange={(e) => setForm((f) => ({ ...f, fecha_limite: e.target.value || null }))}
                />
              </div>
            </div>
            <div className="space-y-2">
              <Label>Categoría (opcional)</Label>
              <Input
                value={form.categoria || ""}
                onChange={(e) => setForm((f) => ({ ...f, categoria: e.target.value || null }))}
                placeholder="Ej: Viajes"
              />
            </div>
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setDialogOpen(false)}>Cancelar</Button>
              <Button type="submit">{editingId ? "Actualizar" : "Crear"}</Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
      <ConfirmDialog
        open={confirmOpen}
        onOpenChange={setConfirmOpen}
        title="Eliminar meta"
        description="¿Estás seguro de que querés eliminar esta meta? Esta acción no se puede deshacer."
        confirmLabel="Eliminar"
        onConfirm={() => {
          if (deleteTargetId) deleteGoal(deleteTargetId);
        }}
      />
    </DashboardLayout>
  );
}
