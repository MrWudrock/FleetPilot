"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useEffect, useState } from "react";

import { fetchHealth } from "@/lib/api";
import { login } from "@/lib/auth";
import { getApiBase, isDesktopApp } from "@/lib/config";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("demo@fleetpilot.ru");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [desktop, setDesktop] = useState(false);
  const [apiUrl, setApiUrl] = useState(getApiBase());
  const [savingApi, setSavingApi] = useState(false);
  const [apiStatus, setApiStatus] = useState<"checking" | "ok" | "down">("checking");

  async function pingApi(base?: string) {
    const url = (base || getApiBase()).replace(/\/$/, "");
    setApiStatus("checking");
    try {
      const prev = window.__FLEETPILOT_API_OVERRIDE__;
      window.__FLEETPILOT_API_OVERRIDE__ = url;
      await fetchHealth();
      setApiStatus("ok");
      if (prev !== undefined) window.__FLEETPILOT_API_OVERRIDE__ = prev;
      else if (!isDesktopApp()) delete window.__FLEETPILOT_API_OVERRIDE__;
    } catch {
      setApiStatus("down");
    }
  }

  useEffect(() => {
    const desk = isDesktopApp();
    setDesktop(desk);
    setApiUrl(getApiBase());
    window.fleetpilotDesktop
      ?.getConfig()
      .then((c) => {
        setApiUrl(c.apiUrl);
        void pingApi(c.apiUrl);
      })
      .catch(() => {
        void pingApi();
      });
    if (!desk) void pingApi();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function applyApiUrl() {
    setSavingApi(true);
    setError(null);
    try {
      let nextUrl = apiUrl.replace(/\/$/, "");
      if (window.fleetpilotDesktop) {
        const next = await window.fleetpilotDesktop.setApiUrl(apiUrl);
        nextUrl = next.apiUrl;
        setApiUrl(nextUrl);
      }
      window.__FLEETPILOT_API_OVERRIDE__ = nextUrl;
      await pingApi(nextUrl);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Не удалось сохранить URL API");
      setApiStatus("down");
    } finally {
      setSavingApi(false);
    }
  }

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    setError(null);

    try {
      if (desktop) {
        await applyApiUrl();
      }
      if (apiStatus === "down") {
        throw new Error("Failed to fetch");
      }
      await login({ email, password });
      router.push("/dashboard");
    } catch (err) {
      const raw = err instanceof Error ? err.message : "Ошибка входа";
      if (/failed to fetch|networkerror|load failed/i.test(raw)) {
        setApiStatus("down");
        setError(
          `Нет связи с API (${getApiBase()}). Сначала запустите backend:\n` +
            `PowerShell в папке проекта → .\\scripts\\start-local.ps1\n` +
            `Проверка: http://localhost:8800/api/v1/health`,
        );
      } else {
        setError(raw);
      }
    } finally {
      setLoading(false);
    }
  }

  const statusColor =
    apiStatus === "ok" ? "text-emerald-400" : apiStatus === "down" ? "text-red-400" : "text-amber-400";
  const statusText =
    apiStatus === "ok" ? "API онлайн" : apiStatus === "down" ? "API недоступен" : "Проверка API…";

  return (
    <main className="flex min-h-screen items-center justify-center bg-zinc-950 px-4" data-testid="login-page">
      <div className="w-full max-w-md rounded-xl border border-zinc-800 bg-zinc-900 p-8 shadow-xl">
        <div className="mb-6 flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-emerald-600 text-sm font-extrabold text-white">
            FP
          </div>
          <div>
            <h1 className="text-xl font-bold text-white">Вход в FleetPilot</h1>
            <p className={`text-sm ${statusColor}`} data-testid="login-api-status">
              {statusText}
            </p>
          </div>
        </div>

        {apiStatus === "down" ? (
          <div
            className="mb-4 whitespace-pre-line rounded-lg border border-red-900/60 bg-red-950/40 px-3 py-2 text-xs text-red-200"
            data-testid="login-api-down"
          >
            Backend не отвечает на {getApiBase()}.
            {"\n"}1. Откройте Docker Desktop (Engine running)
            {"\n"}2. В проекте: .\scripts\start-local.ps1
            {"\n"}3. Обновите статус кнопкой OK у URL API
          </div>
        ) : null}

        <form onSubmit={onSubmit} className="space-y-4" data-testid="login-form">
          <label className="block text-sm">
            <span className="mb-1 block text-zinc-300">URL API</span>
            <div className="flex gap-2">
              <input
                type="url"
                value={apiUrl}
                onChange={(e) => setApiUrl(e.target.value)}
                placeholder="http://localhost:8800"
                className="w-full rounded-md border border-zinc-700 bg-zinc-950 px-3 py-2 font-mono text-sm text-white outline-none ring-emerald-600 focus:ring-2"
                data-testid="login-api-url"
              />
              <button
                type="button"
                disabled={savingApi}
                onClick={() => applyApiUrl()}
                className="shrink-0 rounded-md border border-zinc-600 px-3 text-xs text-zinc-200 hover:bg-zinc-800"
                data-testid="login-api-ok"
              >
                OK
              </button>
            </div>
          </label>

          <label className="block text-sm">
            <span className="mb-1 block text-zinc-300">Email</span>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full rounded-md border border-zinc-700 bg-zinc-950 px-3 py-2 text-white outline-none ring-emerald-600 focus:ring-2"
              data-testid="login-email"
            />
          </label>

          <label className="block text-sm">
            <span className="mb-1 block text-zinc-300">Пароль</span>
            <input
              type="password"
              required
              minLength={8}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full rounded-md border border-zinc-700 bg-zinc-950 px-3 py-2 text-white outline-none ring-emerald-600 focus:ring-2"
              data-testid="login-password"
            />
          </label>

          {error ? (
            <p className="whitespace-pre-line text-sm text-red-400" data-testid="login-error">
              {error}
            </p>
          ) : null}

          <button
            type="submit"
            disabled={loading || apiStatus === "down"}
            className="w-full rounded-md bg-emerald-600 py-2.5 text-sm font-semibold text-white hover:bg-emerald-500 disabled:opacity-60"
            data-testid="login-submit"
          >
            {loading ? "Вход…" : apiStatus === "down" ? "Сначала запустите API" : "Войти"}
          </button>
        </form>

        <p className="mt-6 text-center text-sm text-zinc-400">
          Нет аккаунта?{" "}
          <Link href="/signup" className="text-emerald-400 hover:underline">
            Регистрация
          </Link>
        </p>
      </div>
    </main>
  );
}
