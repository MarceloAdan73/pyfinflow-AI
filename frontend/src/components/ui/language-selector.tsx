"use client";

import { usePathname, useRouter } from "next/navigation";
import { useLocale } from "next-intl";
import { locales, localeNames, defaultLocale, type Locale } from "@/i18n/config";
import { Select } from "@/components/ui/select";
import { Globe } from "lucide-react";

export function LanguageSelector() {
  const locale = useLocale() as Locale;
  const router = useRouter();
  const pathname = usePathname();

  const handleChange = (newLocale: string) => {
    const segments = pathname.split("/").filter(Boolean);
    const hasPrefix = locales.includes(segments[0] as Locale);
    if (hasPrefix) segments.shift();
    if (newLocale !== defaultLocale) segments.unshift(newLocale);
    router.push("/" + segments.join("/"));
  };

  return (
    <div className="flex items-center gap-2">
      <Globe className="h-4 w-4 text-muted-foreground" />
      <Select value={locale} onChange={(e) => handleChange(e.target.value)} className="w-28 text-xs">
        {locales.map((loc) => (
          <option key={loc} value={loc}>
            {localeNames[loc]}
          </option>
        ))}
      </Select>
    </div>
  );
}
