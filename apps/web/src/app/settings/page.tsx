"use client";

import { useEffect, useState } from "react";

import { AppShell } from "@/components/app-shell";
import { AuthGuard } from "@/components/auth-guard";
import type { MeResponse } from "@/lib/auth";
import { getApiBase, isDesktopApp } from "@/lib/config";
import { fetchSettings, updateSettings, type OrgSettings } from "@/lib/fleet";

export default function SettingsPage() {
  return (
    <AuthGuard>
      {(session) => <SettingsContent session={session} />}
    </AuthGuard>
  );
}

function SettingsContent({ session }: { session: MeResponse }) {
  const [name, setName] = useState(session.organization.name);
  const [slug, setSlug] = useState(session.organization.slug);
  const [settings, setSettings] = useState<OrgSettings>({
    timezone: "Europe/Moscow",
    currency: "RUB",
    notify_fuel_email: true,
    notify_maintenance_days: 7,
    demo_mode: true,
    default_origin: "Москва",
  });
  const [apiUrl, setApiUrl] = useState(getApiBase());
  const [desktop, setDesktop] = useState(false);
  const [configPath, setConfigPath] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setDesktop(isDesktopApp());
    setApiUrl(getApiBase());
    window.fleetpilotDesktop
      ?.getDefaults()
      .then((d) => setConfigPath(d.configPath))
      .catch(() => null);
    window.fleetpilotDesktop
      ?.getConfig()
      .then((c) => setApiUrl(c.apiUrl))
      .catch(() => null);

    fetchSettings()
      .then((data) => {
        setName(data.name);
        setSlug(data.slug);
        setSettings(data.settings);
      })
      .catch((e) => setError(String(e)));
  }, []);

  async function onSave(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      if (desktop && window.fleetpilotDesktop) {
        const next = await window.fleetpilotDesktop.setApiUrl(apiUrl);
        setApiUrl(next.apiUrl);
        window.__FLEETPILOT_API_OVERRIDE__ = next.apiUrl;
      }
      const data = await updateSettings({ name, settings });
      setName(data.name);
      setSlug(data.slug);
      setSettings(data.settings);
      setMessage(
        desktop
          ? "Настройки сохранены. URL API применён (при ошибках запросов обновите страницу)."
          : "Настройки сохранены",
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ошибка");
    } finally {
      setLoading(false);
    }
  }

  return (
    <AppShell
      session={session}
      activeHref="/settings"
      title="Настройки"
      subtitle={`Организация · уведомления · ${desktop ? "Desktop" : "Web"}`}
      mainClassName="max-w-2xl space-y-6 p-6"
    >
      {error ? <p className="text-sm text-red-600">{error}</p> : null}
      {message ? <p className="text-sm text-emerald-700">{message}</p> : null}

      <section className="rounded-lg border border-zinc-200 bg-white p-5">
        <h2 className="text-sm font-semibold">Профиль</h2>
        <p className="mt-2 text-sm text-zinc-700">{session.user.full_name}</p>
        <p className="text-xs text-zinc-500">
          {session.user.email} · {session.user.role}
        </p>
      </section>

      <form onSubmit={onSave} className="space-y-4 rounded-lg border border-zinc-200 bg-white p-5">
        <h2 className="text-sm font-semibold">Организация</h2>
        <label className="block text-xs text-zinc-600">
          Название
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="mt-1 w-full rounded-md border border-zinc-300 px-3 py-2 text-sm"
            required
          />
        </label>
        <label className="block text-xs text-zinc-600">
          Slug
          <input
            value={slug}
            disabled
            className="mt-1 w-full rounded-md border border-zinc-200 bg-zinc-50 px-3 py-2 text-sm text-zinc-500"
          />
        </label>

        {desktop ? (
          <label className="block text-xs text-zinc-600">
            URL API
            <input
              value={apiUrl}
              onChange={(e) => setApiUrl(e.target.value)}
              placeholder="http://localhost:8800"
              className="mt-1 w-full rounded-md border border-zinc-300 px-3 py-2 font-mono text-sm"
              required
            />
            <span className="mt-1 block text-[11px] text-zinc-500">
              Сохраняется в конфиг Desktop
              {configPath ? `: ${configPath}` : ""}. Нужен интернет / доступ к серверу FleetPilot.
            </span>
          </label>
        ) : (
          <p className="text-xs text-zinc-500">
            Текущий API: <code className="rounded bg-zinc-100 px-1">{getApiBase()}</code>
          </p>
        )}

        <label className="block text-xs text-zinc-600">
          Часовой пояс
          <input
            value={settings.timezone}
            onChange={(e) => setSettings({ ...settings, timezone: e.target.value })}
            className="mt-1 w-full rounded-md border border-zinc-300 px-3 py-2 text-sm"
          />
        </label>
        <label className="block text-xs text-zinc-600">
          Город по умолчанию (заявки)
          <input
            value={settings.default_origin}
            onChange={(e) => setSettings({ ...settings, default_origin: e.target.value })}
            className="mt-1 w-full rounded-md border border-zinc-300 px-3 py-2 text-sm"
          />
        </label>
        <label className="block text-xs text-zinc-600">
          Предупреждение о ТО за (дней)
          <input
            type="number"
            min={1}
            max={30}
            value={settings.notify_maintenance_days}
            onChange={(e) =>
              setSettings({ ...settings, notify_maintenance_days: Number(e.target.value) || 7 })
            }
            className="mt-1 w-full rounded-md border border-zinc-300 px-3 py-2 text-sm"
          />
        </label>
        <label className="flex items-center gap-2 text-sm text-zinc-700">
          <input
            type="checkbox"
            checked={settings.notify_fuel_email}
            onChange={(e) => setSettings({ ...settings, notify_fuel_email: e.target.checked })}
          />
          Email-уведомления по топливу
        </label>
        <label className="flex items-center gap-2 text-sm text-zinc-700">
          <input
            type="checkbox"
            checked={settings.demo_mode}
            onChange={(e) => setSettings({ ...settings, demo_mode: e.target.checked })}
          />
          DEMO-режим (Wialon / ТМ / маршруты)
        </label>
        <button
          type="submit"
          disabled={loading}
          className="rounded-md bg-zinc-900 px-4 py-2 text-xs font-semibold text-white disabled:opacity-60"
        >
          Сохранить
        </button>
      </form>
    </AppShell>
  );
}
