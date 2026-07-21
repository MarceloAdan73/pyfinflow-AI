"use client";

import { useState, useEffect } from "react";
import { DashboardLayout } from "@/components/layout/dashboard-layout";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { useAuth } from "@/hooks/use-auth";
import { api } from "@/lib/api";
import type { AIProviderSettings, AIStatusResponse } from "@/types";
import {
  User, Key, Bot, Save, Loader2, CheckCircle2, XCircle,
  Settings, Zap, Server, Brain,
} from "lucide-react";
import { PageTransition, StaggerContainer, StaggerItem } from "@/components/ui/motion";

export default function SettingsPage() {
  const { user } = useAuth();
  const [aiSettings, setAiSettings] = useState<AIProviderSettings | null>(null);
  const [aiStatus, setAiStatus] = useState<AIStatusResponse | null>(null);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<"ok" | "fail" | null>(null);

  useEffect(() => {
    api<AIProviderSettings>("/ai/settings").then(setAiSettings).catch(() => {});
    api<AIStatusResponse>("/ai/status").then(setAiStatus).catch(() => {});
  }, []);

  const handleSave = async () => {
    if (!aiSettings) return;
    setSaving(true);
    setSaved(false);
    try {
      const updated = await api<AIProviderSettings>("/ai/settings", { method: "PUT", body: JSON.stringify(aiSettings) });
      setAiSettings(updated);
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } finally {
      setSaving(false);
    }
  };

  const handleTestConnection = async () => {
    setTesting(true);
    setTestResult(null);
    try {
      const status = await api<AIStatusResponse>("/ai/status");
      setAiStatus(status);
      setTestResult(status.active_provider !== "local_rules" ? "ok" : "fail");
    } catch {
      setTestResult("fail");
    } finally {
      setTesting(false);
    }
  };

  const update = (field: keyof AIProviderSettings, value: string | number) => {
    setAiSettings((prev) => (prev ? { ...prev, [field]: value } : prev));
  };

  return (
    <DashboardLayout>
      <PageTransition>
        <StaggerContainer className="space-y-6 max-w-2xl">
          <StaggerItem>
            <div>
              <h1 className="text-2xl font-bold">Configuración</h1>
              <p className="text-muted-foreground">Gestioná tu cuenta y asistente IA</p>
            </div>
          </StaggerItem>

          {/* Profile */}
          <StaggerItem>
            <Card>
              <CardHeader>
                <div className="flex items-center gap-3">
                  <div className="h-10 w-10 rounded-full bg-primary/20 flex items-center justify-center">
                    <User className="h-5 w-5 text-primary" />
                  </div>
                  <div>
                    <CardTitle className="text-base">Perfil</CardTitle>
                    <CardDescription>Información de tu cuenta</CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-muted-foreground">Usuario</p>
                    <p className="font-medium">{user?.username}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Rol</p>
                    <p className="font-medium capitalize">{user?.role}</p>
                  </div>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">ID de usuario</p>
                  <p className="font-mono text-xs text-muted-foreground">{user?.id}</p>
                </div>
              </CardContent>
            </Card>
          </StaggerItem>

          {/* Security */}
          <StaggerItem>
            <Card>
              <CardHeader>
                <div className="flex items-center gap-3">
                  <div className="h-10 w-10 rounded-full bg-amber-500/20 flex items-center justify-center">
                    <Key className="h-5 w-5 text-amber-400" />
                  </div>
                  <div>
                    <CardTitle className="text-base">Seguridad</CardTitle>
                    <CardDescription>Cambiar contraseña</CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  Próximamente podrás cambiar tu contraseña desde aquí.
                </p>
              </CardContent>
            </Card>
          </StaggerItem>

          {/* AI Provider Settings */}
          <StaggerItem>
            <Card>
              <CardHeader>
                <div className="flex items-center gap-3">
                  <div className="h-10 w-10 rounded-full bg-violet-500/20 flex items-center justify-center">
                    <Bot className="h-5 w-5 text-violet-400" />
                  </div>
                  <div className="flex-1">
                    <CardTitle className="text-base">Asistente IA</CardTitle>
                    <CardDescription>Configurá los proveedores de inteligencia artificial</CardDescription>
                  </div>
                  {aiStatus && (
                    <Badge variant={aiStatus.active_provider !== "local_rules" ? "default" : "secondary"}>
                      {aiStatus.active_provider !== "local_rules" ? (
                        <span className="flex items-center gap-1"><CheckCircle2 className="h-3 w-3" /> Activo: {aiStatus.active_provider}</span>
                      ) : (
                        <span className="flex items-center gap-1"><XCircle className="h-3 w-3" /> Sin proveedor activo</span>
                      )}
                    </Badge>
                  )}
                </div>
              </CardHeader>
              <CardContent className="space-y-6">
                {!aiSettings ? (
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <Loader2 className="h-4 w-4 animate-spin" /> Cargando configuración...
                  </div>
                ) : (
                  <>
                    {/* Provider Priority */}
                    <div className="space-y-3">
                      <div className="flex items-center gap-2">
                        <Zap className="h-4 w-4 text-muted-foreground" />
                        <Label className="text-sm font-medium">Prioridad de proveedores</Label>
                      </div>
                      <p className="text-xs text-muted-foreground">
                        Orden en que se intentan los proveedores. El primero disponible será el activo.
                      </p>
                      <Input
                        value={aiSettings.provider_priority}
                        onChange={(e) => update("provider_priority", e.target.value)}
                        placeholder="ollama,huggingface,gemini"
                      />
                    </div>

                    <Separator />

                    {/* Ollama */}
                    <div className="space-y-3">
                      <div className="flex items-center gap-2">
                        <Server className="h-4 w-4 text-muted-foreground" />
                        <Label className="text-sm font-medium">Ollama (local)</Label>
                        {aiStatus?.providers.find((p) => p.name === "ollama")?.available ? (
                          <Badge variant="default" className="text-xs">Conectado</Badge>
                        ) : (
                          <Badge variant="secondary" className="text-xs">No disponible</Badge>
                        )}
                      </div>
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        <div className="space-y-1">
                          <Label className="text-xs text-muted-foreground">URL del servidor</Label>
                          <Input
                            value={aiSettings.ollama_url}
                            onChange={(e) => update("ollama_url", e.target.value)}
                            placeholder="http://localhost:11434"
                          />
                        </div>
                        <div className="space-y-1">
                          <Label className="text-xs text-muted-foreground">Modelo</Label>
                          <Input
                            value={aiSettings.ollama_model}
                            onChange={(e) => update("ollama_model", e.target.value)}
                            placeholder="qwen2.5-coder:7b"
                          />
                        </div>
                      </div>
                    </div>

                    <Separator />

                    {/* HuggingFace */}
                    <div className="space-y-3">
                      <div className="flex items-center gap-2">
                        <Brain className="h-4 w-4 text-muted-foreground" />
                        <Label className="text-sm font-medium">HuggingFace</Label>
                        {aiStatus?.providers.find((p) => p.name === "huggingface")?.available ? (
                          <Badge variant="default" className="text-xs">Conectado</Badge>
                        ) : (
                          <Badge variant="secondary" className="text-xs">No disponible</Badge>
                        )}
                      </div>
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        <div className="space-y-1">
                          <Label className="text-xs text-muted-foreground">Token API</Label>
                          <Input
                            type="password"
                            value={aiSettings.hf_token}
                            onChange={(e) => update("hf_token", e.target.value)}
                            placeholder="hf_xxxxxxxxxxxx"
                          />
                        </div>
                        <div className="space-y-1">
                          <Label className="text-xs text-muted-foreground">Modelo</Label>
                          <Input
                            value={aiSettings.hf_model}
                            onChange={(e) => update("hf_model", e.target.value)}
                            placeholder="HuggingFaceH4/zephyr-7b-beta"
                          />
                        </div>
                      </div>
                    </div>

                    <Separator />

                    {/* Gemini */}
                    <div className="space-y-3">
                      <div className="flex items-center gap-2">
                        <Settings className="h-4 w-4 text-muted-foreground" />
                        <Label className="text-sm font-medium">Google Gemini</Label>
                        {aiStatus?.providers.find((p) => p.name === "gemini")?.available ? (
                          <Badge variant="default" className="text-xs">Conectado</Badge>
                        ) : (
                          <Badge variant="secondary" className="text-xs">No disponible</Badge>
                        )}
                      </div>
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        <div className="space-y-1">
                          <Label className="text-xs text-muted-foreground">API Key</Label>
                          <Input
                            type="password"
                            value={aiSettings.gemini_api_key}
                            onChange={(e) => update("gemini_api_key", e.target.value)}
                            placeholder="AIza..."
                          />
                        </div>
                        <div className="space-y-1">
                          <Label className="text-xs text-muted-foreground">Modelo</Label>
                          <Input
                            value={aiSettings.gemini_model}
                            onChange={(e) => update("gemini_model", e.target.value)}
                            placeholder="gemini-2.0-flash"
                          />
                        </div>
                      </div>
                    </div>

                    <Separator />

                    {/* Generation Parameters */}
                    <div className="space-y-3">
                      <Label className="text-sm font-medium">Parámetros de generación</Label>
                      <div className="grid grid-cols-3 gap-4">
                        <div className="space-y-1">
                          <Label className="text-xs text-muted-foreground">Max tokens</Label>
                          <Input
                            type="number"
                            min={50}
                            max={2000}
                            value={aiSettings.max_tokens}
                            onChange={(e) => update("max_tokens", parseInt(e.target.value) || 500)}
                          />
                        </div>
                        <div className="space-y-1">
                          <Label className="text-xs text-muted-foreground">Temperatura</Label>
                          <Input
                            type="number"
                            min={0}
                            max={2}
                            step={0.1}
                            value={aiSettings.temperature}
                            onChange={(e) => update("temperature", parseFloat(e.target.value) || 0.7)}
                          />
                        </div>
                        <div className="space-y-1">
                          <Label className="text-xs text-muted-foreground">Contexto (msgs)</Label>
                          <Input
                            type="number"
                            min={1}
                            max={100}
                            value={aiSettings.context_window}
                            onChange={(e) => update("context_window", parseInt(e.target.value) || 20)}
                          />
                        </div>
                      </div>
                    </div>

                    <Separator />

                    {/* Embedding Model */}
                    <div className="space-y-3">
                      <Label className="text-sm font-medium">Modelo de embeddings (RAG)</Label>
                      <Input
                        value={aiSettings.embedding_model}
                        onChange={(e) => update("embedding_model", e.target.value)}
                        placeholder="all-MiniLM-L6-v2"
                      />
                      <p className="text-xs text-muted-foreground">
                        Modelo local para generar embeddings de tus transacciones.
                      </p>
                    </div>

                    {/* Actions */}
                    <div className="flex items-center gap-3 pt-2">
                      <Button onClick={handleSave} disabled={saving}>
                        {saving ? (
                          <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                        ) : saved ? (
                          <CheckCircle2 className="h-4 w-4 mr-2" />
                        ) : (
                          <Save className="h-4 w-4 mr-2" />
                        )}
                        {saved ? "Guardado" : "Guardar"}
                      </Button>
                      <Button
                        variant="outline"
                        onClick={handleTestConnection}
                        disabled={testing}
                      >
                        {testing ? (
                          <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                        ) : testResult === "ok" ? (
                          <CheckCircle2 className="h-4 w-4 mr-2 text-emerald-400" />
                        ) : testResult === "fail" ? (
                          <XCircle className="h-4 w-4 mr-2 text-destructive" />
                        ) : (
                          <Zap className="h-4 w-4 mr-2" />
                        )}
                        {testResult === "ok" ? "Conectado" : testResult === "fail" ? "Sin conexión" : "Probar conexión"}
                      </Button>
                    </div>
                  </>
                )}
              </CardContent>
            </Card>
          </StaggerItem>
        </StaggerContainer>
      </PageTransition>
    </DashboardLayout>
  );
}
