"use client";

import { useQuery } from "@tanstack/react-query";

import { AppShell } from "@/components/app-shell";
import { AuthGuard } from "@/components/auth-guard";
import { KpiCards } from "@/components/kpi-cards";
import { SystemStatus } from "@/components/system-status";
import { fetchRoiKpi } from "@/lib/analytics";
import { fetchReadiness } from "@/lib/api";
import type { MeResponse } from "@/lib/auth";
import { queryKeys } from "@/lib/query-keys";

export default function DashboardPage() {
  return (
    <AuthGuard>
      {(session) => <DashboardContent session={session} />}
    </AuthGuard>
  );
}

function DashboardContent({ session }: { session: MeResponse }) {
  const readinessQuery = useQuery({
    queryKey: queryKeys.readiness,
    queryFn: fetchReadiness,
    retry: false,
  });

  const kpiQuery = useQuery({
    queryKey: queryKeys.roi,
    queryFn: fetchRoiKpi,
  });

  const kpi = kpiQuery.data ?? null;

  return (
    <AppShell
      session={session}
      activeHref="/dashboard"
      vehicleCount={kpi?.vehicle_count}
      title="Экономия"
      subtitle={`${session.organization.name} · ${session.user.email}`}
      actions={
        <div
          className="flex h-8 w-8 items-center justify-center rounded-full bg-emerald-100 text-xs font-bold text-emerald-700"
          title={session.user.full_name}
          data-testid="user-avatar"
        >
          {session.user.full_name.charAt(0).toUpperCase()}
        </div>
      }
    >
      <div data-testid="dashboard-kpi">
        <SystemStatus readiness={readinessQuery.data ?? null} />
      </div>
      <KpiCards kpi={kpi} loading={kpiQuery.isLoading} />

      {kpi && kpi.monthly_savings_rub === 0 && kpi.vehicle_count === 0 ? (
        <section className="rounded-lg border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900">
          Пока нет данных по экономии. Подключите телематику в разделе{" "}
          <a href="/integrations" className="font-semibold underline">
            Интеграции
          </a>{" "}
          или попросите администратора загрузить демо-парк.
        </section>
      ) : null}

      <section className="rounded-lg border border-dashed border-zinc-300 bg-white p-6">
        <h2 className="text-sm font-semibold text-zinc-800">Разбивка экономии по агентам</h2>
        {kpi ? (
          <ul className="mt-3 grid gap-2 text-sm text-zinc-600 sm:grid-cols-2 lg:grid-cols-4">
            <li>Fuel Agent: {kpi.breakdown.fuel.toLocaleString("ru-RU")} ₽</li>
            <li>Route Agent: {kpi.breakdown.route.toLocaleString("ru-RU")} ₽</li>
            <li>Dispatch Agent: {kpi.breakdown.dispatch.toLocaleString("ru-RU")} ₽</li>
            <li>Maintenance Agent: {kpi.breakdown.maintenance.toLocaleString("ru-RU")} ₽</li>
          </ul>
        ) : (
          <p className="mt-2 text-sm text-zinc-500">Загрузка…</p>
        )}
      </section>
    </AppShell>
  );
}
