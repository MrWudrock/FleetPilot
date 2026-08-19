"use client";

import { useCallback, useEffect, useState } from "react";

import { AppShell } from "@/components/app-shell";
import { AuthGuard } from "@/components/auth-guard";
import type { MeResponse } from "@/lib/auth";
import {
  analyzeRoute,
  approvePermitRequest,
  checkRosdorPermit,
  fetchRosdorHealth,
  listPermitRequests,
  type PermitAnalysis,
  type PermitRequest,
} from "@/lib/permit";

export default function PilotPage() {
  return (
    <AuthGuard>
      {(session) => <PilotContent session={session} />}
    </AuthGuard>
  );
}

function PilotContent({ session }: { session: MeResponse }) {
  const [origin, setOrigin] = useState("Москва");
  const [destination, setDestination] = useState("Санкт-Петербург");
  const [lengthM, setLengthM] = useState("15");
  const [widthM, setWidthM] = useState("3.2");
  const [heightM, setHeightM] = useState("4.1");
  const [massKg, setMassKg] = useState("48000");
  const [axles, setAxles] = useState("12000,12000");

  const [analysis, setAnalysis] = useState<PermitAnalysis | null>(null);
  const [lastRequestId, setLastRequestId] = useState<string | null>(null);
  const [requests, setRequests] = useState<PermitRequest[]>([]);
  const [rosdorStatus, setRosdorStatus] = useState<string>("…");
  const [permitNumber, setPermitNumber] = useState("DEMO-12345");
  const [plate, setPlate] = useState("А123ВС77");
  const [checkResult, setCheckResult] = useState<string | null>(null);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  const refreshList = useCallback(async () => {
    const data = await listPermitRequests();
    setRequests(data.items);
  }, []);

  useEffect(() => {
    fetchRosdorHealth()
      .then((h) => setRosdorStatus(`${h.status}: ${h.message}`))
      .catch(() => setRosdorStatus("offline"));
    refreshList().catch(() => setRequests([]));
  }, [refreshList]);

  async function onAnalyze(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setMessage(null);
    setLoading(true);
    try {
      const axleLoads = axles
        .split(",")
        .map((s) => Number(s.trim()))
        .filter((n) => !Number.isNaN(n) && n > 0);

      const result = await analyzeRoute({
        origin: { name: origin },
        destination: { name: destination },
        cargo: {
          length_m: Number(lengthM),
          width_m: Number(widthM),
          height_m: Number(heightM),
          mass_kg: Number(massKg),
          axle_loads_kg: axleLoads,
        },
        persist: true,
      });
      setAnalysis(result.analysis);
      setLastRequestId(result.permit_request_id);
      setMessage(
        result.permit_request_id
          ? `Заявка сохранена: ${result.permit_request_id}`
          : "Анализ выполнен (без сохранения)",
      );
      await refreshList();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ошибка");
    } finally {
      setLoading(false);
    }
  }

  async function onApprove(id: string) {
    setError(null);
    setMessage(null);
    setLoading(true);
    try {
      await approvePermitRequest(id, {
        notes: "Проверено в пилотном UI",
        external_permit_number: "PILOT-001",
      });
      setMessage(`Заявка ${id} утверждена`);
      await refreshList();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ошибка утверждения");
    } finally {
      setLoading(false);
    }
  }

  async function onCheckRegistry(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setCheckResult(null);
    setLoading(true);
    try {
      const result = await checkRosdorPermit({
        permit_number: permitNumber,
        plate,
      });
      setCheckResult(
        result.found
          ? `Найдено · ${result.status ?? "—"} · до ${result.valid_until ?? "—"} · ${result.source}`
          : `Не найдено · ${result.source}`,
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ошибка реестра");
    } finally {
      setLoading(false);
    }
  }

  return (
    <AppShell
      session={session}
      activeHref="/pilot"
      title="Разрешения"
      subtitle="Черновик анализа — проверьте и утвердите (HITL)"
      badge={
        <span className="rounded bg-amber-100 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-amber-800">
          DEMO · Permit Agent
        </span>
      }
    >
      <section className="rounded-lg border border-amber-200 bg-amber-50 p-4 text-sm text-amber-950">
        <p className="font-medium">AI-черновик</p>
        <p className="mt-1 text-amber-900">
          Результат агента — предложение для диспетчера, не финальное решение. Всегда проверьте риск и
          утвердите вручную.
        </p>
        <p className="mt-2 text-xs">Статус реестра: {rosdorStatus}</p>
      </section>

      {error ? (
        <p className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p>
      ) : null}
      {message ? (
        <p className="rounded-md border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-emerald-800">
          {message}
        </p>
      ) : null}

      <div className="grid gap-6 lg:grid-cols-2">
        <form id="permit-analyze-form" onSubmit={onAnalyze} className="space-y-3 rounded-lg border border-zinc-200 bg-white p-5">
          <h2 className="text-sm font-semibold text-zinc-800">1. Анализ маршрута (ввод данных пилота)</h2>
          <Field label="Откуда" value={origin} onChange={setOrigin} />
          <Field label="Куда" value={destination} onChange={setDestination} />
          <div className="grid grid-cols-2 gap-3">
            <Field label="Длина, м" value={lengthM} onChange={setLengthM} />
            <Field label="Ширина, м" value={widthM} onChange={setWidthM} />
            <Field label="Высота, м" value={heightM} onChange={setHeightM} />
            <Field label="Масса, кг" value={massKg} onChange={setMassKg} />
          </div>
          <Field label="Оси, кг (через запятую)" value={axles} onChange={setAxles} />
          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-md bg-emerald-600 py-2.5 text-sm font-semibold text-white hover:bg-emerald-500 disabled:opacity-60"
          >
            {loading ? "Анализ…" : "Анализировать и сохранить"}
          </button>
        </form>

        <section className="rounded-lg border border-zinc-200 bg-white p-5">
          <h2 className="text-sm font-semibold text-zinc-800">2. Результат анализа</h2>
          {loading && !analysis ? (
            <div className="mt-3 space-y-2" aria-live="polite" aria-busy="true">
              <p className="text-sm text-zinc-500">Permit Agent анализирует маршрут…</p>
              <div className="h-4 w-3/4 animate-pulse rounded bg-zinc-100" />
              <div className="h-4 w-1/2 animate-pulse rounded bg-zinc-100" />
              <div className="h-20 animate-pulse rounded bg-zinc-100" />
            </div>
          ) : null}
          {!analysis && !loading ? (
            <p className="mt-3 text-sm text-zinc-500">Заполните форму слева и нажмите «Анализировать».</p>
          ) : null}
          {analysis ? (
            <div className="mt-3 space-y-2 text-sm text-zinc-700">
              <p className="rounded-md bg-amber-50 px-2 py-1 text-xs font-medium text-amber-900">
                Черновик агента · требует проверки диспетчера
              </p>
              <p>
                Разрешение нужно:{" "}
                <strong>{analysis.permit_required ? "да" : "нет"}</strong>
              </p>
              <p>
                ПОДД: <strong>{analysis.podd_required ? "да" : "нет"}</strong>
              </p>
              <p>
                Риск: <strong>{analysis.risk_level}</strong> ({analysis.risk_score})
              </p>
              <p>{analysis.route_summary}</p>
              {analysis.restrictions.length > 0 ? (
                <ul className="list-inside list-disc">
                  {analysis.restrictions.map((r) => (
                    <li key={r}>{r}</li>
                  ))}
                </ul>
              ) : null}
              {lastRequestId ? (
                <div className="mt-3 flex flex-wrap gap-2">
                  <button
                    type="button"
                    disabled={loading}
                    onClick={() => onApprove(lastRequestId)}
                    className="min-h-11 rounded-md bg-zinc-900 px-4 py-2 text-xs font-semibold text-white hover:bg-zinc-700 disabled:opacity-60"
                  >
                    Утвердить
                  </button>
                  <button
                    type="submit"
                    form="permit-analyze-form"
                    disabled={loading}
                    className="min-h-11 rounded-md border border-zinc-300 px-4 py-2 text-xs font-medium hover:bg-zinc-50"
                  >
                    Пересчитать
                  </button>
                </div>
              ) : null}
            </div>
          ) : null}
        </section>
      </div>

      <form onSubmit={onCheckRegistry} className="space-y-3 rounded-lg border border-zinc-200 bg-white p-5">
        <h2 className="text-sm font-semibold text-zinc-800">3. Проверка разрешения в реестре (DEMO)</h2>
        <div className="grid gap-3 sm:grid-cols-2">
          <Field label="Номер разрешения" value={permitNumber} onChange={setPermitNumber} />
          <Field label="Госномер" value={plate} onChange={setPlate} />
        </div>
        <button
          type="submit"
          disabled={loading}
          className="rounded-md border border-zinc-300 bg-white px-4 py-2 text-sm font-medium text-zinc-800 hover:bg-zinc-50 disabled:opacity-60"
        >
          Проверить DEMO-12345 / А123ВС77
        </button>
        {checkResult ? <p className="text-sm text-zinc-700">{checkResult}</p> : null}
      </form>

      <section className="rounded-lg border border-zinc-200 bg-white p-5">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-semibold text-zinc-800">4. Заявки Permit ({requests.length})</h2>
          <button
            type="button"
            onClick={() => refreshList().catch((e) => setError(String(e)))}
            className="text-xs text-emerald-700 hover:underline"
          >
            Обновить
          </button>
        </div>
        {requests.length === 0 ? (
          <p className="mt-3 text-sm text-zinc-500">Пока нет заявок — создайте через анализ маршрута.</p>
        ) : (
          <ul className="mt-3 divide-y divide-zinc-100">
            {requests.map((req) => (
              <li key={req.id} className="flex flex-wrap items-center justify-between gap-2 py-3 text-sm">
                <div>
                  <p className="font-medium text-zinc-800">
                    {req.origin.name ?? "?"} → {req.destination.name ?? "?"}
                  </p>
                  <p className="text-xs text-zinc-500">
                    {req.status} · {req.cargo.mass_kg} кг · {new Date(req.created_at).toLocaleString("ru-RU")}
                  </p>
                </div>
                {req.status !== "approved" ? (
                  <button
                    type="button"
                    disabled={loading}
                    onClick={() => onApprove(req.id)}
                    className="rounded-md bg-emerald-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-emerald-500 disabled:opacity-60"
                  >
                    Утвердить
                  </button>
                ) : (
                  <span className="text-xs text-emerald-700">✓ утверждено</span>
                )}
              </li>
            ))}
          </ul>
        )}
      </section>
    </AppShell>
  );
}

function Field({
  label,
  value,
  onChange,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
}) {
  return (
    <label className="block text-xs text-zinc-600">
      {label}
      <input
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="mt-1 w-full rounded-md border border-zinc-300 px-3 py-2 text-sm text-zinc-900 outline-none focus:border-emerald-500"
      />
    </label>
  );
}
