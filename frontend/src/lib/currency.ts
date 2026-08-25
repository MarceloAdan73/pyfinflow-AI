import type { CurrencyCode } from "./utils";

const RATE_CACHE_KEY = "exchange_rates";
const RATE_CACHE_TTL = 60 * 60 * 1000; // 1 hour

interface RateCache {
  rates: Record<string, number>;
  timestamp: number;
}

export async function getExchangeRates(): Promise<Record<CurrencyCode, number>> {
  const cached = getCachedRates();
  if (cached) return cached;

  try {
    const res = await fetch("https://open.er-api.com/v6/latest/USD");
    if (!res.ok) throw new Error("Failed to fetch rates");
    const data = await res.json();
    const rates: Record<CurrencyCode, number> = {
      USD: 1,
      ARS: data.rates.ARS || 1,
      EUR: data.rates.EUR || 1,
      BRL: data.rates.BRL || 1,
    };
    cacheRates(rates);
    return rates;
  } catch {
    return { USD: 1, ARS: 1, EUR: 1, BRL: 1 };
  }
}

export function convertCurrency(
  amount: number,
  from: CurrencyCode,
  to: CurrencyCode,
  rates: Record<CurrencyCode, number>
): number {
  if (from === to) return amount;
  const inUSD = amount / rates[from];
  return inUSD * rates[to];
}

function getCachedRates(): Record<CurrencyCode, number> | null {
  try {
    const raw = localStorage.getItem(RATE_CACHE_KEY);
    if (!raw) return null;
    const cache: RateCache = JSON.parse(raw);
    if (Date.now() - cache.timestamp > RATE_CACHE_TTL) return null;
    return cache.rates as Record<CurrencyCode, number>;
  } catch {
    return null;
  }
}

function cacheRates(rates: Record<CurrencyCode, number>): void {
  try {
    const cache: RateCache = { rates, timestamp: Date.now() };
    localStorage.setItem(RATE_CACHE_KEY, JSON.stringify(cache));
  } catch {
    // ignore
  }
}
