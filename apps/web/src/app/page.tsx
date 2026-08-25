"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { fetchHealth } from "@/lib/api";

export default function HomePage() {
  const [healthLabel, setHealthLabel] = useState("Проверка API…");

  useEffect(() => {
    fetchHealth()
      .then((health) => setHealthLabel(`${health.service} v${health.version} · ${health.status}`))
      .catch(() => setHealthLabel("API offline — проверьте сервер или Настройки"));
  }, []);

  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-6 bg-zinc-950 px-6 text-center text-white">
      <div className="flex h-14 w-14 items-center justify-center rounded-xl bg-emerald-600 text-lg font-extrabold">
        FP
      </div>
      <div>
        <h1 className="text-3xl font-bold">FleetPilot</h1>
        <p className="mt-2 max-w-lg text-zinc-400">
          Desktop / Web · Next.js + FastAPI · пилот автопарка
        </p>
      </div>
      <p className="rounded-full border border-zinc-700 px-4 py-1 text-sm text-zinc-300">{healthLabel}</p>
      <div className="flex flex-wrap justify-center gap-3">
        <Link
          href="/signup"
          className="rounded-md bg-emerald-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-emerald-500"
        >
          Регистрация
        </Link>
        <Link
          href="/login"
          className="rounded-md border border-zinc-700 px-5 py-2.5 text-sm font-semibold text-zinc-200 hover:bg-zinc-900"
        >
          Войти
        </Link>
        <Link
          href="/dashboard"
          className="rounded-md border border-zinc-700 px-5 py-2.5 text-sm font-semibold text-zinc-200 hover:bg-zinc-900"
        >
          Dashboard
        </Link>
        <Link
          href="/pilot"
          className="rounded-md border border-emerald-700 px-5 py-2.5 text-sm font-semibold text-emerald-300 hover:bg-zinc-900"
        >
          Пилот · Permit
        </Link>
      </div>
    </main>
  );
}
