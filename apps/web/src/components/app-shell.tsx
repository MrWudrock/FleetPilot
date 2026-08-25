"use client";

import type { ReactNode } from "react";

import { AuthGuard } from "@/components/auth-guard";
import { PageHeader } from "@/components/page-header";
import { Sidebar } from "@/components/sidebar";
import type { MeResponse } from "@/lib/auth";

type AppShellProps = {
  session: MeResponse;
  activeHref: string;
  vehicleCount?: number;
  title: string;
  subtitle?: string;
  badge?: ReactNode;
  actions?: ReactNode;
  children: ReactNode;
  mainClassName?: string;
};

export function AppShell({
  session,
  activeHref,
  vehicleCount,
  title,
  subtitle,
  badge,
  actions,
  children,
  mainClassName = "flex-1 space-y-6 p-6",
}: AppShellProps) {
  return (
    <div className="flex min-h-screen bg-zinc-100" data-testid="app-shell">
      <Sidebar session={session} vehicleCount={vehicleCount} activeHref={activeHref} />
      <div className="flex min-w-0 flex-1 flex-col">
        <PageHeader title={title} subtitle={subtitle} badge={badge} actions={actions} />
        <main className={mainClassName} data-testid="page-main">
          {children}
        </main>
      </div>
    </div>
  );
}

type AuthenticatedShellProps = Omit<AppShellProps, "session"> & {
  children: ReactNode | ((session: MeResponse) => ReactNode);
};

/** AuthGuard + AppShell. Pass render-prop children to access session. */
export function AuthenticatedShell({
  children,
  ...shell
}: AuthenticatedShellProps) {
  return (
    <AuthGuard>
      {(session) => (
        <AppShell session={session} {...shell}>
          {typeof children === "function" ? children(session) : children}
        </AppShell>
      )}
    </AuthGuard>
  );
}
