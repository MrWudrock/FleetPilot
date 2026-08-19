"use client";

import { useEffect, useState } from "react";

import { AppShell } from "@/components/app-shell";
import { AuthGuard } from "@/components/auth-guard";
import type { MeResponse } from "@/lib/auth";
import {
  completeMaintenanceTask,
  createMaintenanceTask,
  fetchMaintenanceTasks,
  fetchVehicles,
  startMaintenanceTask,
  type MaintenanceTask,
  type Vehicle,
} from "@/lib/fleet";

const KIND_LABEL: Record<string, string> = {
  to: "ТО",
  repair: "Ремонт",
  inspection: "Осмотр",
};

const STATUS_STYLE: Record<string, string> = {
  planned: "border-zinc-200 bg-white",
  overdue: "border-red-300 bg-red-50",
  in_progress: "border-amber-300 bg-amber-50",
  done: "border-emerald-300 bg-emerald-50",
};

export default function MaintenancePage() {
  return (
    <AuthGuard>
      {(session) => <MaintenanceContent session={session} />}
    </AuthGuard>
  );
}

function MaintenanceContent({ session }: { session: MeResponse }) {
  const [items, setItems] = useState<MaintenanceTask[]>([]);
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [overdue, setOverdue] = useState(0);
  const [title, setTitle] = useState("ТО-1 · плановый осмотр");
  const [kind, setKind] = useState("to");
  const [vehicleId, setVehicleId] = useState("");
  const [dueDays, setDueDays] = useState("7");
  const [cost, setCost] = useState("25000");
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function load() {
    const [tasks, fleet] = await Promise.all([fetchMaintenanceTasks(), fetchVehicles()]);
    setItems(tasks.items);
    setOverdue(tasks.overdue);
    setVehicles(fleet.items);
    if (!vehicleId && fleet.items[0]) setVehicleId(fleet.items[0].id);
  }

  useEffect(() => {
    load().catch((e) => setError(String(e)));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function onCreate(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const due = new Date();
      due.setDate(due.getDate() + Number(dueDays || 0));
      await createMaintenanceTask({
        title,
        kind,
        vehicle_id: vehicleId || undefined,
        due_at: due.toISOString(),
        estimated_cost_rub: Number(cost) || undefined,
        notes: "Создано из UI пилота",
      });
      setMessage("Задача ТО создана");
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ошибка");
    } finally {
      setLoading(false);
    }
  }

  async function run(action: () => Promise<unknown>, ok: string) {
    setLoading(true);
    setError(null);
    try {
      await action();
      setMessage(ok);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ошибка");
    } finally {
      setLoading(false);
    }
  }

  return (
    <AppShell
      session={session}
      activeHref="/maintenance"
      title="ТО и ремонт"
      subtitle={`Maintenance Agent · просрочено: ${overdue} · всего: ${items.length}`}
    >
      {error ? <p className="text-sm text-red-600">{error}</p> : null}
      {message ? <p className="text-sm text-emerald-700">{message}</p> : null}

      <form onSubmit={onCreate} className="rounded-lg border border-zinc-200 bg-white p-5">
        <h2 className="text-sm font-semibold">Новая задача</h2>
        <div className="mt-3 grid gap-3 md:grid-cols-2 lg:grid-cols-4">
          <label className="text-xs text-zinc-600">
            Название
            <input
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="mt-1 w-full rounded-md border border-zinc-300 px-3 py-2 text-sm"
              required
            />
          </label>
          <label className="text-xs text-zinc-600">
            Тип
            <select
              value={kind}
              onChange={(e) => setKind(e.target.value)}
              className="mt-1 w-full rounded-md border border-zinc-300 px-3 py-2 text-sm"
            >
              <option value="to">ТО</option>
              <option value="repair">Ремонт</option>
              <option value="inspection">Осмотр</option>
            </select>
          </label>
          <label className="text-xs text-zinc-600">
            ТС
            <select
              value={vehicleId}
              onChange={(e) => setVehicleId(e.target.value)}
              className="mt-1 w-full rounded-md border border-zinc-300 px-3 py-2 text-sm"
            >
              {vehicles.map((v) => (
                <option key={v.id} value={v.id}>
                  {v.plate} · {v.brand} {v.model}
                </option>
              ))}
            </select>
          </label>
          <label className="text-xs text-zinc-600">
            Через дней / стоимость ₽
            <div className="mt-1 flex gap-2">
              <input
                value={dueDays}
                onChange={(e) => setDueDays(e.target.value)}
                className="w-full rounded-md border border-zinc-300 px-3 py-2 text-sm"
              />
              <input
                value={cost}
                onChange={(e) => setCost(e.target.value)}
                className="w-full rounded-md border border-zinc-300 px-3 py-2 text-sm"
              />
            </div>
          </label>
        </div>
        <button
          type="submit"
          disabled={loading}
          className="mt-4 rounded-md bg-zinc-900 px-4 py-2 text-xs font-semibold text-white disabled:opacity-60"
        >
          Создать
        </button>
      </form>

      <ul className="space-y-3">
        {items.map((t) => (
          <li
            key={t.id}
            className={`rounded-lg border p-4 ${STATUS_STYLE[t.status] ?? "border-zinc-200 bg-white"}`}
          >
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <p className="text-xs uppercase tracking-wide text-zinc-500">
                  {KIND_LABEL[t.kind] ?? t.kind} · {t.status}
                </p>
                <p className="font-medium text-zinc-900">{t.title}</p>
                <p className="mt-1 text-xs text-zinc-600">
                  {t.plate ?? "ТС н/д"}
                  {t.due_at ? ` · до ${new Date(t.due_at).toLocaleDateString("ru-RU")}` : ""}
                  {t.mileage_km != null
                    ? ` · ${Math.round(t.mileage_km).toLocaleString("ru-RU")} км`
                    : ""}
                  {t.estimated_cost_rub != null
                    ? ` · ₽${t.estimated_cost_rub.toLocaleString("ru-RU")}`
                    : ""}
                </p>
                {t.notes ? <p className="mt-1 text-[11px] text-zinc-500">{t.notes}</p> : null}
              </div>
              <div className="flex gap-2">
                {t.status !== "done" && t.status !== "in_progress" ? (
                  <button
                    type="button"
                    disabled={loading}
                    onClick={() => run(() => startMaintenanceTask(t.id), "В работе")}
                    className="rounded-md border border-zinc-300 px-3 py-1.5 text-xs font-medium hover:bg-white"
                  >
                    В работу
                  </button>
                ) : null}
                {t.status !== "done" ? (
                  <button
                    type="button"
                    disabled={loading}
                    onClick={() => run(() => completeMaintenanceTask(t.id), "Закрыто")}
                    className="rounded-md bg-zinc-900 px-3 py-1.5 text-xs font-semibold text-white disabled:opacity-60"
                  >
                    Закрыть
                  </button>
                ) : (
                  <span className="text-xs font-semibold text-emerald-700">готово</span>
                )}
              </div>
            </div>
          </li>
        ))}
      </ul>
    </AppShell>
  );
}
