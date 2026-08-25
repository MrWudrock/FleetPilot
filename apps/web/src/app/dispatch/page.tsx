"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

import { AppShell } from "@/components/app-shell";
import { AuthGuard } from "@/components/auth-guard";
import type { MeResponse } from "@/lib/auth";
import {
  assignOrder,
  createOrder,
  fetchOrders,
  fetchVehicles,
  syncTransManager,
} from "@/lib/fleet";
import { queryKeys } from "@/lib/query-keys";

export default function DispatchPage() {
  return (
    <AuthGuard>
      {(session) => <DispatchContent session={session} />}
    </AuthGuard>
  );
}

function DispatchContent({ session }: { session: MeResponse }) {
  const queryClient = useQueryClient();
  const [origin, setOrigin] = useState("Москва");
  const [destination, setDestination] = useState("Казань");
  const [mass, setMass] = useState("18000");
  const [message, setMessage] = useState<string | null>(null);
  const [formError, setFormError] = useState<string | null>(null);
  const [assignVehicle, setAssignVehicle] = useState<Record<string, string>>({});

  const ordersQuery = useQuery({
    queryKey: queryKeys.orders,
    queryFn: fetchOrders,
  });

  const vehiclesQuery = useQuery({
    queryKey: queryKeys.vehicles,
    queryFn: fetchVehicles,
  });

  async function invalidateFleet() {
    await Promise.all([
      queryClient.invalidateQueries({ queryKey: queryKeys.orders }),
      queryClient.invalidateQueries({ queryKey: queryKeys.vehicles }),
      queryClient.invalidateQueries({ queryKey: queryKeys.routes }),
    ]);
  }

  const syncMutation = useMutation({
    mutationFn: syncTransManager,
    onSuccess: async (res) => {
      setMessage(res.message);
      await invalidateFleet();
    },
  });

  const createMutation = useMutation({
    mutationFn: createOrder,
    onSuccess: async () => {
      setMessage("Заявка создана");
      await invalidateFleet();
    },
  });

  const assignMutation = useMutation({
    mutationFn: ({ orderId, vehicleId }: { orderId: string; vehicleId: string }) =>
      assignOrder(orderId, vehicleId),
    onSuccess: async () => {
      setMessage("ТС назначено");
      await invalidateFleet();
    },
  });

  const orders = ordersQuery.data?.items ?? [];
  const vehicles = (vehiclesQuery.data?.items ?? []).filter((x) => x.status === "active");
  const loading =
    ordersQuery.isFetching ||
    syncMutation.isPending ||
    createMutation.isPending ||
    assignMutation.isPending;
  const error =
    formError ||
    (ordersQuery.error instanceof Error ? ordersQuery.error.message : null) ||
    (syncMutation.error instanceof Error ? syncMutation.error.message : null) ||
    (createMutation.error instanceof Error ? createMutation.error.message : null) ||
    (assignMutation.error instanceof Error ? assignMutation.error.message : null);

  function onCreate(e: React.FormEvent) {
    e.preventDefault();
    setFormError(null);
    createMutation.mutate({
      origin_name: origin,
      destination_name: destination,
      mass_kg: Number(mass),
      length_m: 13.6,
      width_m: 2.45,
      height_m: 3.8,
      notes: "Пилотная заявка из UI",
    });
  }

  function onAssign(orderId: string) {
    const vehicleId = assignVehicle[orderId];
    if (!vehicleId) {
      setFormError("Выберите ТС");
      return;
    }
    setFormError(null);
    assignMutation.mutate({ orderId, vehicleId });
  }

  return (
    <AppShell
      session={session}
      activeHref="/dispatch"
      title="Диспетчеризация · ТрансМенеджер"
      subtitle="Заявки DEMO · назначение ТС"
      actions={
        <button
          type="button"
          disabled={loading}
          onClick={() => syncMutation.mutate()}
          className="min-h-11 rounded-md bg-emerald-600 px-3 py-2 text-xs font-semibold text-white disabled:opacity-60"
          data-testid="dispatch-sync"
        >
          Sync ТМ
        </button>
      }
    >
      {error ? <p className="text-sm text-red-600">{error}</p> : null}
      {message ? <p className="text-sm text-emerald-700">{message}</p> : null}

      <form
        onSubmit={onCreate}
        className="grid gap-3 rounded-lg border border-zinc-200 bg-white p-5 sm:grid-cols-4"
        data-testid="dispatch-create-form"
      >
        <h2 className="text-sm font-semibold sm:col-span-4">Новая заявка (пилот)</h2>
        <label className="text-xs">
          Откуда
          <input
            className="mt-1 w-full rounded-md border px-2 py-1.5 text-sm"
            value={origin}
            onChange={(e) => setOrigin(e.target.value)}
          />
        </label>
        <label className="text-xs">
          Куда
          <input
            className="mt-1 w-full rounded-md border px-2 py-1.5 text-sm"
            value={destination}
            onChange={(e) => setDestination(e.target.value)}
          />
        </label>
        <label className="text-xs">
          Масса, кг
          <input
            className="mt-1 w-full rounded-md border px-2 py-1.5 text-sm"
            value={mass}
            onChange={(e) => setMass(e.target.value)}
          />
        </label>
        <button
          type="submit"
          disabled={loading}
          className="min-h-11 self-end rounded-md bg-zinc-900 py-2 text-xs font-semibold text-white disabled:opacity-60"
        >
          Создать
        </button>
      </form>

      <section className="rounded-lg border border-zinc-200 bg-white" data-testid="dispatch-orders">
        <div className="border-b border-zinc-100 px-5 py-3 text-sm font-semibold">
          Заявки ({orders.length})
        </div>
        <ul className="divide-y divide-zinc-100">
          {orders.map((o) => (
            <li
              key={o.id}
              className="flex flex-wrap items-center justify-between gap-3 px-5 py-3 text-sm"
            >
              <div>
                <p className="font-medium">
                  {o.external_ref} · {o.details.origin?.name ?? "?"} →{" "}
                  {o.details.destination?.name ?? "?"}
                </p>
                <p className="text-xs text-zinc-500">
                  {o.status}
                  {o.details.plate ? ` · ${o.details.plate}` : ""}
                  {o.details.cargo?.mass_kg ? ` · ${o.details.cargo.mass_kg} кг` : ""}
                  {" · "}
                  {new Date(o.created_at).toLocaleString("ru-RU")}
                </p>
              </div>
              {o.status === "new" || o.status === "assigned" ? (
                <div className="flex items-center gap-2">
                  <select
                    className="min-h-11 rounded-md border border-zinc-300 px-2 py-1 text-xs"
                    value={assignVehicle[o.id] ?? ""}
                    onChange={(e) =>
                      setAssignVehicle((s) => ({ ...s, [o.id]: e.target.value }))
                    }
                  >
                    <option value="">ТС…</option>
                    {vehicles.map((v) => (
                      <option key={v.id} value={v.id}>
                        {v.plate} · {v.brand}
                      </option>
                    ))}
                  </select>
                  <button
                    type="button"
                    disabled={loading}
                    onClick={() => onAssign(o.id)}
                    className="min-h-11 rounded-md bg-emerald-600 px-2 py-1 text-xs font-semibold text-white disabled:opacity-60"
                  >
                    Назначить
                  </button>
                </div>
              ) : null}
            </li>
          ))}
        </ul>
      </section>
    </AppShell>
  );
}
