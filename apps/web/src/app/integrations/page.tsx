"use client";

import { useEffect, useState } from "react";

import { AppShell } from "@/components/app-shell";
import { AuthGuard } from "@/components/auth-guard";
import type { MeResponse } from "@/lib/auth";
import {
  connectTransManager,
  connectWialon,
  fetchIntegrations,
  syncTransManager,
  syncWialon,
  type Integration,
} from "@/lib/fleet";

export default function IntegrationsPage() {
  return (
    <AuthGuard>
      {(session) => <IntegrationsContent session={session} />}
    </AuthGuard>
  );
}

function IntegrationsContent({ session }: { session: MeResponse }) {
  const [items, setItems] = useState<Integration[]>([]);
  const [token, setToken] = useState("demo-token");
  const [host, setHost] = useState("https://wialon.local");
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function load() {
    const data = await fetchIntegrations();
    setItems(data.items);
  }

  useEffect(() => {
    load().catch((e) => setError(String(e)));
  }, []);

  async function run(action: () => Promise<unknown>, okMsg: string) {
    setLoading(true);
    setError(null);
    setMessage(null);
    try {
      const result = await action();
      setMessage(typeof result === "object" && result && "message" in result ? String((result as { message: string }).message) : okMsg);
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Ошибка");
    } finally {
      setLoading(false);
    }
  }

  return (
    <AppShell
      session={session}
      activeHref="/integrations"
      title="Интеграции"
      subtitle="Wialon Local · ТрансМенеджер · DEMO-режим для пилота"
    >
      {error ? <p className="text-sm text-red-600">{error}</p> : null}
      {message ? <p className="text-sm text-emerald-700">{message}</p> : null}

      <div className="grid gap-4 lg:grid-cols-2">
        <section className="rounded-lg border border-zinc-200 bg-white p-5">
          <h2 className="text-sm font-semibold">Wialon Local</h2>
          <p className="mt-1 text-xs text-zinc-500">
            В DEMO принимается любой token. Sync обновляет координаты всех ТС на карте.
          </p>
          <label className="mt-3 block text-xs text-zinc-600">
            Host
            <input
              value={host}
              onChange={(e) => setHost(e.target.value)}
              className="mt-1 w-full rounded-md border border-zinc-300 px-3 py-2 text-sm"
            />
          </label>
          <label className="mt-2 block text-xs text-zinc-600">
            API token
            <input
              value={token}
              onChange={(e) => setToken(e.target.value)}
              className="mt-1 w-full rounded-md border border-zinc-300 px-3 py-2 text-sm"
            />
          </label>
          <div className="mt-3 flex gap-2">
            <button
              type="button"
              disabled={loading}
              onClick={() => run(() => connectWialon(token, host, true), "Wialon подключён")}
              className="rounded-md bg-emerald-600 px-3 py-2 text-xs font-semibold text-white disabled:opacity-60"
            >
              Подключить
            </button>
            <button
              type="button"
              disabled={loading}
              onClick={() => run(() => syncWialon(), "Sync OK")}
              className="rounded-md border border-zinc-300 px-3 py-2 text-xs font-medium disabled:opacity-60"
            >
              Sync позиции
            </button>
          </div>
        </section>

        <section className="rounded-lg border border-zinc-200 bg-white p-5">
          <h2 className="text-sm font-semibold">ТрансМенеджер</h2>
          <p className="mt-1 text-xs text-zinc-500">
            DEMO sync подтягивает / дополняет заявки для экрана «Диспетчеризация».
          </p>
          <div className="mt-3 flex gap-2">
            <button
              type="button"
              disabled={loading}
              onClick={() => run(() => connectTransManager(token, true), "ТМ подключён")}
              className="rounded-md bg-emerald-600 px-3 py-2 text-xs font-semibold text-white disabled:opacity-60"
            >
              Подключить
            </button>
            <button
              type="button"
              disabled={loading}
              onClick={() => run(() => syncTransManager(), "Sync OK")}
              className="rounded-md border border-zinc-300 px-3 py-2 text-xs font-medium disabled:opacity-60"
            >
              Sync заявки
            </button>
          </div>
        </section>
      </div>

      <section className="rounded-lg border border-zinc-200 bg-white p-5">
        <h2 className="mb-3 text-sm font-semibold">Статус подключений</h2>
        {items.length === 0 ? (
          <p className="text-sm text-zinc-500">Пока нет интеграций — нажмите «Подключить».</p>
        ) : (
          <ul className="divide-y divide-zinc-100 text-sm">
            {items.map((i) => (
              <li key={i.id} className="flex flex-wrap items-center justify-between gap-2 py-3">
                <div>
                  <p className="font-medium">{i.label}</p>
                  <p className="text-xs text-zinc-500">
                    {i.provider} · {i.demo ? "DEMO" : "live"} · sync{" "}
                    {i.last_sync_at ? new Date(i.last_sync_at).toLocaleString("ru-RU") : "—"}
                  </p>
                </div>
                <span
                  className={`rounded-full px-2 py-0.5 text-xs font-semibold ${
                    i.status === "active"
                      ? "bg-emerald-100 text-emerald-800"
                      : "bg-zinc-100 text-zinc-600"
                  }`}
                >
                  {i.status}
                </span>
              </li>
            ))}
          </ul>
        )}
      </section>
    </AppShell>
  );
}
