"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { FormEvent, Suspense, useState } from "react";

import { acceptInvite } from "@/lib/auth";

function AcceptInviteForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [token, setToken] = useState(searchParams.get("token") ?? "");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    setError(null);

    try {
      await acceptInvite({ token, password });
      router.push("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ошибка принятия приглашения");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={onSubmit} className="space-y-4">
      <label className="block text-sm">
        <span className="mb-1 block text-zinc-300">Invite token</span>
        <input
          required
          value={token}
          onChange={(e) => setToken(e.target.value)}
          className="w-full rounded-md border border-zinc-700 bg-zinc-950 px-3 py-2 text-white outline-none ring-emerald-600 focus:ring-2"
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
        />
      </label>

      {error ? <p className="text-sm text-red-400">{error}</p> : null}

      <button
        type="submit"
        disabled={loading}
        className="w-full rounded-md bg-emerald-600 py-2.5 text-sm font-semibold text-white hover:bg-emerald-500 disabled:opacity-60"
      >
        {loading ? "Сохранение…" : "Принять приглашение"}
      </button>
    </form>
  );
}

export default function AcceptInvitePage() {
  return (
    <main className="flex min-h-screen items-center justify-center bg-zinc-950 px-4">
      <div className="w-full max-w-md rounded-xl border border-zinc-800 bg-zinc-900 p-8 shadow-xl">
        <h1 className="mb-2 text-xl font-bold text-white">Приглашение в команду</h1>
        <p className="mb-6 text-sm text-zinc-400">Установите пароль для завершения регистрации</p>

        <Suspense fallback={<p className="text-sm text-zinc-400">Загрузка…</p>}>
          <AcceptInviteForm />
        </Suspense>

        <p className="mt-6 text-center text-sm text-zinc-400">
          <Link href="/login" className="text-emerald-400 hover:underline">
            Вернуться ко входу
          </Link>
        </p>
      </div>
    </main>
  );
}
