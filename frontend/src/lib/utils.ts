import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export const CURRENCIES = {
  ARS: { symbol: "$", locale: "es-AR", name: "Peso argentino" },
  USD: { symbol: "$", locale: "en-US", name: "US Dollar" },
  EUR: { symbol: "€", locale: "de-DE", name: "Euro" },
  BRL: { symbol: "R$", locale: "pt-BR", name: "Real brasileño" },
} as const;

export type CurrencyCode = keyof typeof CURRENCIES;

export function formatMoney(amount: number, currency: CurrencyCode = "ARS"): string {
  const config = CURRENCIES[currency] || CURRENCIES.ARS;
  return new Intl.NumberFormat(config.locale, {
    style: "currency",
    currency: currency,
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  }).format(amount);
}

export function formatDate(dateStr: string): string {
  const [year, month, day] = dateStr.split("-");
  return `${day}/${month}/${year}`;
}

export function getCurrentMonth(): string {
  const now = new Date();
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}`;
}
