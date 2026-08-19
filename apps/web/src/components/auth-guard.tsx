"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { fetchMe, getToken, type MeResponse } from "@/lib/auth";

type AuthGuardProps = {
  children: (session: MeResponse) => React.ReactNode;
};

export function AuthGuard({ children }: AuthGuardProps) {
  const router = useRouter();
  const [session, setSession] = useState<MeResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!getToken()) {
      router.replace("/login");
      return;
    }

    fetchMe()
      .then(setSession)
      .catch(() => {
        setError("Сессия истекла");
        router.replace("/login");
      });
  }, [router]);

  if (error) {
    return null;
  }

  if (!session) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-zinc-100 text-sm text-zinc-500">
        Загрузка…
      </div>
    );
  }

  return <>{children(session)}</>;
}
