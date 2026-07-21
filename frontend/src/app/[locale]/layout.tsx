import type { Metadata } from "next";
import { Providers } from "@/components/layout/providers";
import "../globals.css";

export const metadata: Metadata = {
  title: "PyStreamFlow | Fintech AI",
  description: "Plataforma de gestión financiera personal con IA",
};

const themeScript = `
  (function() {
    try {
      var theme = localStorage.getItem('theme');
      if (theme === 'light') {
        document.documentElement.classList.remove('dark');
        document.documentElement.classList.add('light');
      }
    } catch(e) {}
  })()
`;

export default function LocaleLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: themeScript }} />
      </head>
      <body className="min-h-full flex flex-col bg-background text-foreground antialiased dark">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
