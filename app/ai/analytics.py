import statistics
from collections import defaultdict

import structlog

logger = structlog.get_logger()


class FinancialAnalytics:
    """Análisis predictivo: tendencias, predicciones y anomalías"""

    def analizar_tendencias(
        self, transactions: list[dict]
    ) -> dict:
        """Analiza tendencia de gasto por categoría (sube/baja/estable)"""
        if not transactions:
            return {}

        gastos_por_mes = defaultdict(lambda: defaultdict(float))
        for txn in transactions:
            if txn.get("tipo") != "Gasto":
                continue
            fecha = txn.get("fecha", "")
            cat = txn.get("categoria", "Otro")
            monto = float(txn.get("monto", 0))
            if len(fecha) >= 7:
                mes = fecha[:7]
                gastos_por_mes[cat][mes] += monto

        tendencias = {}
        for cat, meses in gastos_por_mes.items():
            sorted_months = sorted(meses.keys())
            if len(sorted_months) < 2:
                tendencias[cat] = {"trend": "stable", "change_pct": 0.0}
                continue

            values = [meses[m] for m in sorted_months]
            first_half = statistics.mean(values[: len(values) // 2]) if len(values) > 1 else values[0]
            second_half = statistics.mean(values[len(values) // 2 :]) if len(values) > 1 else values[0]

            if first_half == 0:
                change_pct = 100.0 if second_half > 0 else 0.0
            else:
                change_pct = ((second_half - first_half) / first_half) * 100

            if change_pct > 10:
                trend = "up"
            elif change_pct < -10:
                trend = "down"
            else:
                trend = "stable"

            tendencias[cat] = {
                "trend": trend,
                "change_pct": round(change_pct, 1),
                "promedio": round(statistics.mean(values), 2),
            }

        return tendencias

    def predecir_gasto_mensual(self, transactions: list[dict]) -> dict:
        """Predice gasto del próximo mes basándose en histórico"""
        gastos_por_mes = defaultdict(float)
        for txn in transactions:
            if txn.get("tipo") != "Gasto":
                continue
            fecha = txn.get("fecha", "")
            monto = float(txn.get("monto", 0))
            if len(fecha) >= 7:
                gastos_por_mes[fecha[:7]] += monto

        sorted_months = sorted(gastos_por_mes.keys())
        if not sorted_months:
            return {"prediccion": 0, "confianza": 0.0, "metodo": "sin_datos"}

        values = [gastos_por_mes[m] for m in sorted_months]

        if len(values) >= 3:
            recent = values[-3:]
            weights = [0.2, 0.3, 0.5]
            prediccion = sum(v * w for v, w in zip(recent, weights))
            std_dev = statistics.stdev(recent) if len(recent) > 1 else 0
            mean_val = statistics.mean(recent)
            cv = (std_dev / mean_val * 100) if mean_val > 0 else 100
            confianza = max(0.3, min(0.95, 1 - cv / 100))
            metodo = "weighted_avg_3m"
        elif len(values) >= 2:
            prediccion = statistics.mean(values)
            confianza = 0.5
            metodo = "avg_2m"
        else:
            prediccion = values[0]
            confianza = 0.3
            metodo = "single_month"

        return {
            "prediccion": round(prediccion, 2),
            "confianza": round(confianza, 2),
            "metodo": metodo,
            "historico": {m: round(gastos_por_mes[m], 2) for m in sorted_months[-6:]},
        }

    def detectar_anomalias(
        self, transactions: list[dict], umbral: float = 2.0
    ) -> list[dict]:
        """Detecta gastos anómalos (>N desviaciones estándar por categoría)"""
        gastos_por_cat = defaultdict(list)
        for txn in transactions:
            if txn.get("tipo") != "Gasto":
                continue
            cat = txn.get("categoria", "Otro")
            monto = float(txn.get("monto", 0))
            gastos_por_cat[cat].append(monto)

        anomalias = []
        for txn in transactions:
            if txn.get("tipo") != "Gasto":
                continue
            cat = txn.get("categoria", "Otro")
            monto = float(txn.get("monto", 0))
            valores = gastos_por_cat[cat]

            if len(valores) < 3:
                continue

            mean_val = statistics.mean(valores)
            std_dev = statistics.stdev(valores)

            if std_dev == 0:
                continue

            z_score = (monto - mean_val) / std_dev

            if abs(z_score) > umbral:
                anomalias.append({
                    "id": txn.get("id"),
                    "categoria": cat,
                    "monto": monto,
                    "fecha": txn.get("fecha"),
                    "descripcion": txn.get("descripcion", ""),
                    "z_score": round(z_score, 2),
                    "promedio_categoria": round(mean_val, 2),
                    "reason": (
                        f"Gasto de ${monto:,.2f} en {cat} es "
                        f"{abs(z_score):.1f} desviaciones estándar "
                        f"por encima del promedio (${mean_val:,.2f})"
                    ),
                })

        return sorted(anomalias, key=lambda x: abs(x["z_score"]), reverse=True)

    def generar_insights(
        self, transactions: list[dict]
    ) -> list[str]:
        """Genera insights automáticos basados en datos"""
        insights = []

        tendencias = self.analizar_tendencias(transactions)
        for cat, data in tendencias.items():
            if data["trend"] == "up" and abs(data["change_pct"]) > 15:
                insights.append(
                    f"Tu gasto en {cat} subió {data['change_pct']:.0f}% "
                    f"últimamente vs el período anterior."
                )
            elif data["trend"] == "down" and abs(data["change_pct"]) > 15:
                insights.append(
                    f"¡Bien! Tu gasto en {cat} bajó {abs(data['change_pct']):.0f}% "
                    f"últimamente."
                )

        prediccion = self.predecir_gasto_mensual(transactions)
        if prediccion["prediccion"] > 0 and prediccion["confianza"] > 0.5:
            insights.append(
                f"Basado en tu histórico, vas a gastar ~${prediccion['prediccion']:,.2f} "
                f"este mes (confianza: {prediccion['confianza']:.0%})."
            )

        anomalias = self.detectar_anomalias(transactions)
        for anom in anomalias[:2]:
            insights.append(
                f"Detectamos un gasto inusual de ${anom['monto']:,.2f} en "
                f"{anom['categoria']} el {anom.get('fecha', 'N/A')}."
            )

        gastos = [t for t in transactions if t.get("tipo") == "Gasto"]
        ingresos = [t for t in transactions if t.get("tipo") == "Ingreso"]
        total_gastos = sum(float(t.get("monto", 0)) for t in gastos)
        total_ingresos = sum(float(t.get("monto", 0)) for t in ingresos)

        if total_ingresos > 0:
            ratio = (total_gastos / total_ingresos) * 100
            if ratio > 90:
                insights.append(
                    f"Estás gastando el {ratio:.0f}% de tus ingresos. "
                    f"Intenta reducir gastos para ahorrar más."
                )
            elif ratio < 60:
                insights.append(
                    f"Excelente! Solo estás gastando el {ratio:.0f}% de tus ingresos. "
                    f"Buen ritmo de ahorro."
                )

        if not insights:
            insights.append(
                "Agrega más transacciones para obtener insights personalizados."
            )

        return insights
