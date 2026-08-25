"use client";

import { useState, useCallback } from "react";
import type { CurrencyCode } from "./utils";

const CURRENCY_KEY = "preferred_currency";
const VALID: readonly CurrencyCode[] = ["ARS", "USD", "EUR", "BRL"];

function readStored(): CurrencyCode {
  if (typeof window === "undefined") return "ARS";
  try {
    const stored = localStorage.getItem(CURRENCY_KEY);
    if (stored && (VALID as readonly string[]).includes(stored)) {
      return stored as CurrencyCode;
    }
  } catch {
    // ignore
  }
  return "ARS";
}

export function useCurrency(): [CurrencyCode, (c: CurrencyCode) => void] {
  const [currency, setCurrencyState] = useState<CurrencyCode>(readStored);

  const setCurrency = useCallback((c: CurrencyCode) => {
    setCurrencyState(c);
    try {
      localStorage.setItem(CURRENCY_KEY, c);
    } catch {
      // ignore
    }
  }, []);

  return [currency, setCurrency];
}
