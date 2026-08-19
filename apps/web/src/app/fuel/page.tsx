"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { AppShell } from "@/components/app-shell";
import { AuthGuard } from "@/components/auth-guard";
import type { MeResponse } from "@/lib/auth";
import { acknowledgeFuelAlert, fetchFuelAlerts } from "@/lib/fleet";
import { queryKeys } from "@/lib/query-keys";

export default function FuelPage() {
  return (
    <AuthGuard>
      {(session) => <FuelContent session={session} />}
    </AuthGuard>
  );
}

function FuelContent({ session }: { session: MeResponse }) {
  const queryClient = useQueryClient();

  const alertsQuery = useQuery({
    queryKey: queryKeys.fuelAlerts,
    queryFn: fetchFuelAlerts,
  });

  const ackMutation = useMutation({
    mutationFn: acknowledgeFuelAlert,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: queryKeys.fuelAlerts }),
  });

  const alerts = alertsQuery.data?.items ?? [];
  const unack = alertsQuery.data?.unacknowledged ?? 0;
  const error =
    alertsQuery.error instanceof Error
      ? alertsQuery.error.message
      : ackMutation.error instanceof Error
        ? ackMutation.error.message
        : null;
  const loading = alertsQuery.isFetching || ackMutation.isPending;

  const severityColor: Record<string, string> = {
    critical: "border-red-300 bg-red-50 text-red-900",
    warning: "border-amber-300 bg-amber-50 text-amber-900",
    info: "border-sky-300 bg-sky-50 text-sky-900",
  };

  return (
    <AppShell
      session={session}
      activeHref="/fuel"
      title="Топливо"
      subtitle={`Алерты топлива · неподтверждённых: ${unack}`}
      actions={
        <button
          type="button"
          onClick={() => alertsQuery.refetch()}
          disabled={loading}
          className="min-h-11 rounded-md border border-zinc-300 px-3 py-2 text-xs font-medium hover:bg-zinc-50"
          data-testid="fuel-refresh"
        >
          Обновить
        </button>
      }
      mainClassName="space-y-4 p-6"
    >
      {error ? <p className="text-sm text-red-600">{error}</p> : null}
      {alerts.length === 0 && !alertsQuery.isLoading ? (
        <div className="rounded-lg border border-zinc-200 bg-white p-5 text-sm text-zinc-600">
          <p className="font-medium text-zinc-800">Нет топливных алертов</p>
          <p className="mt-1">
            Синхронизируйте телематику в{" "}
            <a href="/integrations" className="font-medium text-emerald-700 underline">
              Интеграциях
            </a>
            , чтобы получать сливы и перерасход.
          </p>
        </div>
      ) : (
        <ul className="space-y-3" data-testid="fuel-alerts-list">
          {alerts.map((a) => (
            <li
              key={a.id}
              className={`rounded-lg border p-4 ${severityColor[a.severity] ?? "border-zinc-200 bg-white"}`}
            >
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <p className="text-xs uppercase tracking-wide opacity-70">{a.severity}</p>
                  <p className="font-medium">{a.title}</p>
                  <p className="mt-1 text-xs opacity-80">
                    {a.plate ?? "ТС н/д"} · {new Date(a.detected_at).toLocaleString("ru-RU")}
                  </p>
                </div>
                {a.acknowledged ? (
                  <span className="text-xs font-semibold">✓ подтверждено</span>
                ) : (
                  <button
                    type="button"
                    disabled={loading}
                    onClick={() => ackMutation.mutate(a.id)}
                    className="min-h-11 rounded-md bg-zinc-900 px-3 py-2 text-xs font-semibold text-white disabled:opacity-60"
                    data-testid={`fuel-ack-${a.id}`}
                  >
                    Подтвердить
                  </button>
                )}
              </div>
            </li>
          ))}
        </ul>
      )}
    </AppShell>
  );
}
