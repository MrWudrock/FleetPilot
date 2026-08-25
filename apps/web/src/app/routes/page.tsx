"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

import { AppShell } from "@/components/app-shell";
import { AuthGuard } from "@/components/auth-guard";
import type { MeResponse } from "@/lib/auth";
import { acceptRoute, fetchRoutes, optimizeRoute } from "@/lib/fleet";
import { queryKeys } from "@/lib/query-keys";

export default function RoutesPage() {
  return (
    <AuthGuard>
      {(session) => <RoutesContent session={session} />}
    </AuthGuard>
  );
}

function RoutesContent({ session }: { session: MeResponse }) {
  const queryClient = useQueryClient();
  const [message, setMessage] = useState<string | null>(null);

  const routesQuery = useQuery({
    queryKey: queryKeys.routes,
    queryFn: fetchRoutes,
  });

  const optimizeMutation = useMutation({
    mutationFn: optimizeRoute,
    onSuccess: async () => {
      setMessage("Route Agent: варианты маршрута готовы");
      await queryClient.invalidateQueries({ queryKey: queryKeys.routes });
    },
  });

  const acceptMutation = useMutation({
    mutationFn: ({ orderId, variantId }: { orderId: string; variantId: string }) =>
      acceptRoute(orderId, variantId),
    onSuccess: async (_data, vars) => {
      setMessage(`Маршрут «${vars.variantId}» принят`);
      await queryClient.invalidateQueries({ queryKey: queryKeys.routes });
    },
  });

  const items = routesQuery.data?.items ?? [];
  const loading =
    routesQuery.isFetching || optimizeMutation.isPending || acceptMutation.isPending;
  const error =
    routesQuery.error instanceof Error
      ? routesQuery.error.message
      : optimizeMutation.error instanceof Error
        ? optimizeMutation.error.message
        : acceptMutation.error instanceof Error
          ? acceptMutation.error.message
          : null;

  return (
    <AppShell
      session={session}
      activeHref="/routes"
      title="Маршруты"
      subtitle="Черновик маршрута — проверьте и примите вариант"
      badge={
        <span className="rounded bg-amber-100 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-amber-800">
          DEMO · Route Agent
        </span>
      }
      actions={
        <button
          type="button"
          onClick={() => routesQuery.refetch()}
          disabled={loading}
          className="min-h-11 rounded-md border border-zinc-300 px-3 py-2 text-xs font-medium hover:bg-zinc-50"
        >
          Обновить
        </button>
      }
      mainClassName="space-y-4 p-6"
    >
      {error ? <p className="text-sm text-red-600">{error}</p> : null}
      {message ? <p className="text-sm text-emerald-700">{message}</p> : null}
      {loading ? (
        <p className="text-sm text-zinc-500" aria-live="polite">
          Route Agent считает варианты…
        </p>
      ) : null}
      {items.length === 0 && !routesQuery.isLoading ? (
        <div className="rounded-lg border border-zinc-200 bg-white p-5 text-sm text-zinc-600">
          <p className="font-medium text-zinc-800">Нет активных заявок</p>
          <p className="mt-1">
            Создайте заявку в{" "}
            <a href="/dispatch" className="font-medium text-emerald-700 underline">
              Диспетчеризации
            </a>
            , затем оптимизируйте маршрут здесь.
          </p>
        </div>
      ) : null}
      {items.length > 0 ? (
        <ul className="space-y-4" data-testid="routes-list">
          {items.map((r) => (
            <li key={r.order_id} className="rounded-lg border border-zinc-200 bg-white p-4">
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <p className="text-xs uppercase tracking-wide text-zinc-500">
                    {r.external_ref ?? r.order_id.slice(0, 8)} · {r.status}
                  </p>
                  <p className="mt-1 font-medium text-zinc-900">
                    {r.origin} → {r.destination}
                  </p>
                  <p className="mt-1 text-xs text-zinc-500">
                    ТС: {r.plate ?? "не назначено"}
                    {r.accepted_variant_id
                      ? ` · принят: ${r.accepted_variant_id}`
                      : r.recommended
                        ? ` · рекомендован: ${r.recommended}`
                        : ""}
                  </p>
                </div>
                <button
                  type="button"
                  disabled={loading}
                  onClick={() => optimizeMutation.mutate(r.order_id)}
                  className="min-h-11 rounded-md bg-zinc-900 px-3 py-2 text-xs font-semibold text-white disabled:opacity-60"
                >
                  {optimizeMutation.isPending ? "Считаю…" : "Оптимизировать"}
                </button>
              </div>
              {r.variants.length > 0 ? (
                <div className="mt-4 grid gap-3 md:grid-cols-3">
                  {r.variants.map((v) => {
                    const accepted = r.accepted_variant_id === v.id;
                    const recommended = r.recommended === v.id;
                    return (
                      <div
                        key={v.id}
                        className={`rounded-md border p-3 ${
                          accepted
                            ? "border-emerald-400 bg-emerald-50"
                            : recommended
                              ? "border-sky-300 bg-sky-50"
                              : "border-zinc-200"
                        }`}
                      >
                        <p className="text-sm font-semibold">
                          {v.label}
                          {recommended ? (
                            <span className="ml-2 text-[10px] uppercase text-sky-700">рек. агентом</span>
                          ) : null}
                        </p>
                        <p className="mt-1 text-xs text-zinc-600">
                          {v.distance_km} км · {v.duration_h} ч
                        </p>
                        <p className="text-xs text-zinc-600">
                          топливо ₽{v.fuel_cost_rub.toLocaleString("ru-RU")} · экономия ₽
                          {v.savings_rub.toLocaleString("ru-RU")}
                        </p>
                        <p className="mt-1 text-[11px] text-zinc-500">{v.via.join(" · ")}</p>
                        {!accepted ? (
                          <div className="mt-2 flex flex-wrap gap-2">
                            <button
                              type="button"
                              disabled={loading}
                              onClick={() =>
                                acceptMutation.mutate({ orderId: r.order_id, variantId: v.id })
                              }
                              className="min-h-11 rounded-md bg-emerald-700 px-3 py-2 text-xs font-semibold text-white disabled:opacity-60"
                            >
                              Принять
                            </button>
                            <button
                              type="button"
                              disabled={loading}
                              onClick={() => optimizeMutation.mutate(r.order_id)}
                              className="min-h-11 rounded-md border border-zinc-300 px-3 py-2 text-xs font-medium hover:bg-zinc-50"
                            >
                              Пересчитать
                            </button>
                          </div>
                        ) : (
                          <p className="mt-2 text-[11px] font-semibold text-emerald-700">
                            принят диспетчером
                          </p>
                        )}
                      </div>
                    );
                  })}
                </div>
              ) : null}
            </li>
          ))}
        </ul>
      ) : null}
    </AppShell>
  );
}
