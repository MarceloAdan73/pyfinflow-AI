import { NextRequest, NextResponse } from "next/server";
import createMiddleware from "next-intl/middleware";
import { locales, defaultLocale } from "./i18n/config";

const intlMiddleware = createMiddleware({
  locales,
  defaultLocale,
  localePrefix: "as-needed",
});

export default function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const segments = pathname.split("/").filter(Boolean);

  // Detecta una ruta con prefijo de idioma (/es/register, /en/register) o sin él
  const hasLocale = locales.includes(segments[0] as (typeof locales)[number]);
  const pathWithoutLocale = "/" + (hasLocale ? segments.slice(1) : segments).join("/");

  // El registro público está deshabilitado en el demo: redirigir a login
  if (pathWithoutLocale === "/register") {
    const target = new URL((hasLocale ? `/${segments[0]}` : "") + "/login", request.url);
    return NextResponse.redirect(target);
  }

  return intlMiddleware(request);
}

export const config = {
  matcher: ["/((?!api|_next|_vercel|.*\\..*).*)"],
};
