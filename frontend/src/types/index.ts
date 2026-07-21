export interface User {
  id: string;
  username: string;
  role: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface Transaction {
  id: string;
  user_id: string;
  tipo: "Ingreso" | "Gasto";
  monto: number;
  categoria: string;
  descripcion: string;
  fecha: string;
  moneda: string;
  created_at: string | null;
}

export interface TransactionCreate {
  tipo: "Ingreso" | "Gasto";
  monto: number;
  categoria: string;
  descripcion?: string;
  fecha: string;
  moneda?: string;
}

export interface TransactionUpdate {
  tipo?: "Ingreso" | "Gasto";
  monto?: number;
  categoria?: string;
  descripcion?: string;
  fecha?: string;
  moneda?: string;
}

export interface Budget {
  id: string;
  user_id: string;
  categoria: string;
  limite: number;
  mes: string;
}

export interface BudgetCreate {
  categoria: string;
  limite: number;
  mes: string;
}

export interface Goal {
  id: string;
  user_id: string;
  nombre: string;
  objetivo: number;
  ahorrado: number;
  fecha_limite: string | null;
  categoria: string | null;
}

export interface GoalCreate {
  nombre: string;
  objetivo: number;
  fecha_limite?: string | null;
  categoria?: string | null;
}

export interface GoalUpdate {
  nombre?: string;
  objetivo?: number;
  ahorrado?: number;
  fecha_limite?: string | null;
  categoria?: string | null;
}

export interface ChatMessage {
  id: string;
  user_id: string;
  role: "user" | "assistant";
  content: string;
  provider: string | null;
  tokens_used: number;
  created_at: string | null;
}

export interface AIResponse {
  respuesta: string;
  provider: string;
  contexto_usado: number;
  latency_ms: number;
}

export interface InsightTrend {
  trend: "up" | "down" | "stable";
  change_pct: number;
  promedio: number;
}

export interface InsightPrediction {
  prediccion: number;
  confianza: number;
  metodo: string;
  historico: Record<string, number>;
}

export interface InsightAnomaly {
  id: string | null;
  categoria: string;
  monto: number;
  fecha: string | null;
  z_score: number;
  reason: string;
}

export interface InsightResponse {
  tendencias: Record<string, InsightTrend>;
  prediccion: InsightPrediction;
  anomalias: InsightAnomaly[];
  insights: string[];
}

export interface AIStatusResponse {
  providers: { name: string; available: boolean }[];
  active_provider: string;
  chromadb_available: boolean;
}
