"use client";

import { DashboardLayout } from "@/components/layout/dashboard-layout";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { useAuth } from "@/hooks/use-auth";
import { User, Key } from "lucide-react";
import { PageTransition, StaggerContainer, StaggerItem } from "@/components/ui/motion";

export default function SettingsPage() {
  const { user } = useAuth();

  return (
    <DashboardLayout>
      <PageTransition>
        <StaggerContainer className="space-y-6 max-w-2xl">
          <StaggerItem>
            <div>
              <h1 className="text-2xl font-bold">Configuración</h1>
              <p className="text-muted-foreground">Gestioná tu cuenta</p>
            </div>
          </StaggerItem>

          <StaggerItem>
            <Card>
              <CardHeader>
                <div className="flex items-center gap-3">
                  <div className="h-10 w-10 rounded-full bg-primary/20 flex items-center justify-center">
                    <User className="h-5 w-5 text-primary" />
                  </div>
                  <div>
                    <CardTitle className="text-base">Perfil</CardTitle>
                    <CardDescription>Información de tu cuenta</CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-muted-foreground">Usuario</p>
                    <p className="font-medium">{user?.username}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Rol</p>
                    <p className="font-medium capitalize">{user?.role}</p>
                  </div>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">ID de usuario</p>
                  <p className="font-mono text-xs text-muted-foreground">{user?.id}</p>
                </div>
              </CardContent>
            </Card>
          </StaggerItem>

          <StaggerItem>
            <Card>
              <CardHeader>
                <div className="flex items-center gap-3">
                  <div className="h-10 w-10 rounded-full bg-amber-500/20 flex items-center justify-center">
                    <Key className="h-5 w-5 text-amber-400" />
                  </div>
                  <div>
                    <CardTitle className="text-base">Seguridad</CardTitle>
                    <CardDescription>Cambiar contraseña</CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  Próximamente podrás cambiar tu contraseña desde aquí.
                </p>
              </CardContent>
            </Card>
          </StaggerItem>
        </StaggerContainer>
      </PageTransition>
    </DashboardLayout>
  );
}
