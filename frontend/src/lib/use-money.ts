"use client";

import { useEffect, useState, useCallback } from "react";
import type { CurrencyCode } from "./utils";
import { getExchangeRates, convertCurrency } from "./currency";
import { useCurrency } from "./use-currency";

export function useMoney() {
  const [displayCurrency, setDisplayCurrency] = useCurrency();
  const [rates, setRates] = useState<Record<CurrencyCode, number>>({
    USD: 1,
    ARS: 1,
    EUR: 1,
    BRL: 1,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    getExchangeRates().then((r) => {
      if (mounted) {
        setRates(r);
        setLoading(false);
      }
    });
    return () => {
      mounted = false;
    };
  }, []);

  const formatMoney = useCallback(
    (amount: number, fromCurrency?: CurrencyCode) => {
      const from = fromCurrency || displayCurrency;
      if (from === displayCurrency) {
        const config = {
          ARS: { symbol: "$", locale: "es-AR" },
          USD: { symbol: "$", locale: "en-US" },
          EUR: { symbol: "€", locale: "de-DE" },
          BRL: { symbol: "R$", locale: "pt-BR" },
        }[displayCurrency] || { symbol: "$", locale: "es-AR" };
        return new Intl.NumberFormat(config.locale, {
          style: "currency",
          currency: displayCurrency,
          minimumFractionDigits: 0,
          maximumFractionDigits: 2,
        }).format(amount);
      }
      const converted = convertCurrency(amount, from, displayCurrency, rates);
      const config = {
        ARS: { symbol: "$", locale: "es-AR" },
        USD: { symbol: "$", locale: "en-US" },
        EUR: { symbol: "€", locale: "de-DE" },
        BRL: { symbol: "R$", locale: "pt-BR" },
      }[displayCurrency] || { symbol: "$", locale: "es-AR" };
      return new Intl.NumberFormat(config.locale, {
        style: "currency",
        currency: displayCurrency,
        minimumFractionDigits: 0,
        maximumFractionDigits: 2,
      }).format(converted);
    },
    [displayCurrency, rates]
  );

  return { formatMoney, displayCurrency, setDisplayCurrency, rates, loading };
}

export function useFormatMoney() {
  const { formatMoney } = useMoney();
  return formatMoney;
}