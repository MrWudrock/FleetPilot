"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";

import { signup } from "@/lib/auth";

export default function SignupPage() {
  const router = useRouter();
  const [form, setForm] = useState({
    email: "",
    password: "",
    full_name: "",
    organization_name: "",
  });
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    setError(null);

    try {
      await signup(form);
      router.push("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ошибка регистрации");
    } finally {
      setLoading(false);
    }
  }

  function updateField(field: keyof typeof form, value: string) {
    setForm((prev) => ({ ...prev, [field]: value }));
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-zinc-950 px-4 py-10">
      <div className="w-full max-w-md rounded-xl border border-zinc-800 bg-zinc-900 p-8 shadow-xl">
        <div className="mb-6">
          <h1 className="text-xl font-bold text-white">Регистрация</h1>
          <p className="mt-1 text-sm text-zinc-400">Создайте организацию и аккаунт администратора</p>
        </div>

        <form onSubmit={onSubmit} className="space-y-4">
          <label className="block text-sm">
            <span className="mb-1 block text-zinc-300">Компания</span>
            <input
              required
              value={form.organization_name}
              onChange={(e) => updateField("organization_name", e.target.value)}
              className="w-full rounded-md border border-zinc-700 bg-zinc-950 px-3 py-2 text-white outline-none ring-emerald-600 focus:ring-2"
              placeholder="ООО ТрансЛогистик"
            />
          </label>

          <label className="block text-sm">
            <span className="mb-1 block text-zinc-300">Ваше имя</span>
            <input
              required
              value={form.full_name}
              onChange={(e) => updateField("full_name", e.target.value)}
              className="w-full rounded-md border border-zinc-700 bg-zinc-950 px-3 py-2 text-white outline-none ring-emerald-600 focus:ring-2"
            />
          </label>

          <label className="block text-sm">
            <span className="mb-1 block text-zinc-300">Email</span>
            <input
              type="email"
              required
              value={form.email}
              onChange={(e) => updateField("email", e.target.value)}
              className="w-full rounded-md border border-zinc-700 bg-zinc-950 px-3 py-2 text-white outline-none ring-emerald-600 focus:ring-2"
            />
          </label>

          <label className="block text-sm">
            <span className="mb-1 block text-zinc-300">Пароль (мин. 8 символов)</span>
            <input
              type="password"
              required
              minLength={8}
              value={form.password}
              onChange={(e) => updateField("password", e.target.value)}
              className="w-full rounded-md border border-zinc-700 bg-zinc-950 px-3 py-2 text-white outline-none ring-emerald-600 focus:ring-2"
            />
          </label>

          {error ? <p className="text-sm text-red-400">{error}</p> : null}

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-md bg-emerald-600 py-2.5 text-sm font-semibold text-white hover:bg-emerald-500 disabled:opacity-60"
          >
            {loading ? "Создание…" : "Создать аккаунт"}
          </button>
        </form>

        <p className="mt-6 text-center text-sm text-zinc-400">
          Уже есть аккаунт?{" "}
          <Link href="/login" className="text-emerald-400 hover:underline">
            Войти
          </Link>
        </p>
      </div>
    </main>
  );
}
