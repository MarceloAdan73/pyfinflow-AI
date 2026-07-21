"use client";

import Link from "next/link";
import { useTranslations } from "next-intl";
import { Button } from "@/components/ui/button";
import { PageTransition } from "@/components/ui/motion";
import { Home, ArrowLeft } from "lucide-react";

export default function NotFound() {
  const t = useTranslations("notFound");

  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <PageTransition>
        <div className="text-center space-y-6 px-4">
          <div className="space-y-2">
            <h1 className="text-7xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
              404
            </h1>
            <p className="text-xl text-muted-foreground">{t("title")}</p>
            <p className="text-sm text-muted-foreground max-w-md mx-auto">
              {t("description")}
            </p>
          </div>
          <div className="flex items-center justify-center gap-3">
            <Button variant="outline" onClick={() => window.history.back()} className="gap-2">
              <ArrowLeft className="h-4 w-4" /> {t("back")}
            </Button>
            <Link href="/dashboard">
              <Button className="gap-2">
                <Home className="h-4 w-4" /> Dashboard
              </Button>
            </Link>
          </div>
        </div>
      </PageTransition>
    </div>
  );
}
