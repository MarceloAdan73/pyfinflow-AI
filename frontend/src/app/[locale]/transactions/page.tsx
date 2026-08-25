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
import { useKeyboardShortcuts } from "@/hooks/use-keyboard-shortcuts";
import { formatMoney, formatDate } from "@/lib/utils";
import type { TransactionCreate } from "@/types";
import { Plus, Trash2, Edit, Filter, Search, Upload, FileText } from "lucide-react";
import { PageTransition, StaggerContainer, StaggerItem } from "@/components/ui/motion";
import { ConfirmDialog } from "@/components/ui/confirm-dialog";
import { useTranslations } from "next-intl";

const categorias = [
  "Alimentación", "Transporte", "Servicios", "Ocio", "Salud",
  "Educación", "Ropa", "Hogar", "Salary", "Freelance", "Inversiones", "Otros",
];

export default function TransactionsPage() {
  const t = useTranslations("transactions");
  const tc = useTranslations("common");
  const [filters, setFilters] = useState<Record<string, string>>({});
  const [search, setSearch] = useState("");
  const [dialogOpen, setDialogOpen] = useState(false);
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [deleteTargetId, setDeleteTargetId] = useState<string | null>(null);
  const [editingId, setEditingId] = useState<string | null>(null);
  const { transactions, isLoading, createTransaction, updateTransaction, deleteTransaction, importTransactions } = useTransactions(filters);
  const [importOpen, setImportOpen] = useState(false);
  const [importFile, setImportFile] = useState<File | null>(null);
  const [importPreview, setImportPreview] = useState<string[][] | null>(null);
  const [importResult, setImportResult] = useState<{ imported: number; skipped: number; errors: { row: number; detail: string }[] } | null>(null);
  const [importLoading, setImportLoading] = useState(false);

  const filteredTransactions = transactions.filter((txn) => {
    if (!search) return true;
    const q = search.toLowerCase();
    return (
      txn.descripcion?.toLowerCase().includes(q) ||
      txn.categoria?.toLowerCase().includes(q)
    );
  });

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

  useKeyboardShortcuts({
    "Ctrl+n": openCreate,
    "Ctrl+f": () => {
      const searchInput = document.querySelector<HTMLInputElement>('input[placeholder*="Buscar"]');
      searchInput?.focus();
    },
  });

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
    setDeleteTargetId(id);
    setConfirmOpen(true);
  };

  const handleImportFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0] || null;
    setImportFile(f);
    setImportResult(null);
    if (!f) { setImportPreview(null); return; }
    const text = await f.text();
    const lines = text.split(/\r?\n/).filter(Boolean).slice(0, 6); // header + 5 preview
    setImportPreview(lines.map((l) => l.split(/[,;]/).map((c) => c.trim().replace(/^"|"$/g, ""))));
  };

  const handleImport = async () => {
    if (!importFile) return;
    setImportLoading(true);
    try {
      const res = await importTransactions(importFile);
      setImportResult(res);
    } catch (err: unknown) {
      setImportResult({ imported: 0, skipped: 0, errors: [{ row: 0, detail: err instanceof Error ? err.message : "Error desconocido" }] });
    } finally {
      setImportLoading(false);
    }
  };

  return (
    <DashboardLayout>
      <PageTransition>
        <StaggerContainer className="space-y-6">
          <StaggerItem>
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-2xl font-bold">{t("title")}</h1>
                <p className="text-muted-foreground">{t("description")}</p>
              </div>
              <div className="flex gap-2">
                <Button variant="outline" onClick={() => setImportOpen(true)} className="gap-2">
                  <Upload className="h-4 w-4" /> {t("import")}
                </Button>
                <Button onClick={openCreate} className="gap-2">
                  <Plus className="h-4 w-4" /> {t("new")}
                </Button>
              </div>
            </div>
          </StaggerItem>

          <StaggerItem>
            <Card>
              <CardHeader>
                <div className="flex items-center gap-2">
                  <div className="relative flex-1 max-w-xs">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input
                      value={search}
                      onChange={(e) => setSearch(e.target.value)}
                      placeholder={t("searchPlaceholder")}
                      className="pl-9"
                    />
                  </div>
                  <Filter className="h-4 w-4 text-muted-foreground" />
                  <Select
                    value={filters.tipo || ""}
                    onChange={(e) => setFilters((f) => ({ ...f, tipo: e.target.value }))}
                    className="w-40"
                  >
                    <option value="">{t("filterAll")}</option>
                    <option value="Ingreso">{t("filterIncome")}</option>
                    <option value="Gasto">{t("filterExpenses")}</option>
                  </Select>
                  <Select
                    value={filters.categoria || ""}
                    onChange={(e) => setFilters((f) => ({ ...f, categoria: e.target.value }))}
                    className="w-48"
                  >
                    <option value="">{t("allCategories")}</option>
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
                ) : filteredTransactions.length === 0 ? (
                  <p className="text-center text-muted-foreground py-8">
                    {search ? t("noResults") : t("empty")}
                  </p>
                ) : (
                  <div className="space-y-2">
                    {filteredTransactions.map((txn) => (
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
            <DialogTitle>{editingId ? t("editTitle") : t("newTitle")}</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>{t("type")}</Label>
                <Select
                  value={form.tipo}
                  onChange={(e) => setForm((f) => ({ ...f, tipo: e.target.value as "Ingreso" | "Gasto" }))}
                >
                  <option value="Ingreso">{t("typeIncome")}</option>
                  <option value="Gasto">{t("typeExpense")}</option>
                </Select>
              </div>
              <div className="space-y-2">
                <Label>{t("amount")}</Label>
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
                <Label>{t("category")}</Label>
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
                <Label>{t("date")}</Label>
                <Input
                  type="date"
                  value={form.fecha}
                  onChange={(e) => setForm((f) => ({ ...f, fecha: e.target.value }))}
                  required
                />
              </div>
            </div>
            <div className="space-y-2">
              <Label>{t("description")}</Label>
              <Input
                value={form.descripcion}
                onChange={(e) => setForm((f) => ({ ...f, descripcion: e.target.value }))}
                placeholder={t("descriptionPlaceholder")}
              />
            </div>
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setDialogOpen(false)}>{tc("cancel")}</Button>
              <Button type="submit">{editingId ? tc("update") : tc("create")}</Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
      <Dialog open={importOpen} onOpenChange={(o) => { setImportOpen(o); if (!o) { setImportFile(null); setImportPreview(null); setImportResult(null); } }}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2"><FileText className="h-4 w-4" /> {t("importTitle")}</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <p className="text-sm text-muted-foreground">{t("importDescription")}</p>
            <div className="rounded-md bg-secondary/50 p-3 text-xs font-mono">
              fecha,tipo,monto,categoria,descripcion,moneda<br />2026-07-19,Gasto,1500,Comida,Almuerzo,ARS
            </div>
            <Input type="file" accept=".csv" onChange={handleImportFile} />
            {importPreview && (
              <div className="rounded border overflow-auto max-h-40 text-xs">
                <table className="w-full">
                  <tbody>
                    {importPreview.map((row, i) => (
                      <tr key={i} className={i === 0 ? "bg-secondary font-semibold" : ""}>
                        {row.map((c, j) => <td key={j} className="px-2 py-1 border-b whitespace-nowrap">{c}</td>)}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
            {importResult && (
              <div className={`rounded p-3 text-sm ${importResult.errors.length ? "bg-amber-50 dark:bg-amber-950/30" : "bg-emerald-50 dark:bg-emerald-950/30"}`}>
                <p>{t("importResult", { imported: importResult.imported, skipped: importResult.skipped })}</p>
                {importResult.errors.length > 0 && (
                  <ul className="mt-2 list-disc pl-5 text-xs space-y-1">
                    {importResult.errors.slice(0, 5).map((e, i) => <li key={i}>Fila {e.row}: {e.detail}</li>)}
                    {importResult.errors.length > 5 && <li>... +{importResult.errors.length - 5} más</li>}
                  </ul>
                )}
              </div>
            )}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setImportOpen(false)}>{tc("close")}</Button>
            <Button onClick={handleImport} disabled={!importFile || importLoading}>{importLoading ? tc("loading") : t("importAction")}</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <ConfirmDialog
        open={confirmOpen}
        onOpenChange={setConfirmOpen}
        title={t("deleteTitle")}
        description={t("deleteDescription")}
        confirmLabel={tc("delete")}
        onConfirm={() => {
          if (deleteTargetId) deleteTransaction(deleteTargetId);
        }}
      />
    </DashboardLayout>
  );
}
