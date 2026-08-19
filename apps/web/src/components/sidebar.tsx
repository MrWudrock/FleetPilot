"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { logout, type MeResponse } from "@/lib/auth";

type NavItem = { href: string; label: string };

export const navGroups: { title: string; items: NavItem[] }[] = [
  {
    title: "Операции",
    items: [
      { href: "/dispatch", label: "Диспетчеризация" },
      { href: "/map", label: "Карта автопарка" },
      { href: "/routes", label: "Маршруты" },
      { href: "/fuel", label: "Топливо" },
    ],
  },
  {
    title: "Автопарк",
    items: [{ href: "/maintenance", label: "ТО и ремонт" }],
  },
  {
    title: "Аналитика",
    items: [
      { href: "/dashboard", label: "Экономия (ROI)" },
      { href: "/pilot", label: "Разрешения" },
    ],
  },
  {
    title: "Система",
    items: [
      { href: "/integrations", label: "Интеграции" },
      { href: "/settings", label: "Настройки" },
    ],
  },
];

type SidebarProps = {
  session: MeResponse;
  vehicleCount?: number;
  activeHref?: string;
};

function NavBody({
  activeHref,
  onNavigate,
}: {
  activeHref: string;
  onNavigate?: () => void;
}) {
  return (
    <nav className="flex-1 overflow-y-auto py-3" aria-label="Основное меню">
      {navGroups.map((group) => (
        <div key={group.title} className="mb-3">
          <p className="px-5 pb-1 text-[10px] font-semibold uppercase tracking-wider text-zinc-500">
            {group.title}
          </p>
          {group.items.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              onClick={onNavigate}
              className={`block min-h-11 border-l-2 px-5 py-2.5 text-sm transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-[-2px] focus-visible:outline-accent ${
                activeHref === item.href
                  ? "border-accent bg-zinc-800 font-medium text-white"
                  : "border-transparent text-zinc-300 hover:bg-zinc-800"
              }`}
              data-testid={`nav-${item.href.replace(/^\//, "")}`}
            >
              {item.label}
            </Link>
          ))}
        </div>
      ))}
    </nav>
  );
}

function SidebarChrome({
  session,
  vehicleCount,
  activeHref,
  onNavigate,
  onClose,
}: SidebarProps & { onNavigate?: () => void; onClose?: () => void }) {
  return (
    <div className="flex h-full w-64 flex-col border-r border-surface-border bg-surface">
      <div className="flex items-center justify-between border-b border-surface-border px-5 py-5">
        <div className="flex items-center gap-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-md bg-accent text-xs font-extrabold text-white">
            FP
          </div>
          <div>
            <p className="text-sm font-semibold text-white">FleetPilot</p>
            <p className="text-xs text-surface-muted">{session.organization.name}</p>
          </div>
        </div>
        {onClose ? (
          <button
            type="button"
            onClick={onClose}
            className="flex h-11 w-11 items-center justify-center rounded-md text-zinc-300 hover:bg-zinc-800 focus-visible:outline focus-visible:outline-2 focus-visible:outline-accent md:hidden"
            aria-label="Закрыть меню"
          >
            ✕
          </button>
        ) : null}
      </div>

      <NavBody activeHref={activeHref ?? "/dashboard"} onNavigate={onNavigate} />

      <div className="border-t border-surface-border px-5 py-4">
        <p className="text-xs text-zinc-300">{session.user.full_name}</p>
        <p className="text-xs text-surface-muted">
          {vehicleCount !== undefined ? `${vehicleCount} ТС` : session.user.role}
        </p>
        <button
          type="button"
          onClick={logout}
          className="mt-2 flex min-h-11 items-center rounded-md px-2 text-sm font-medium text-emerald-400 hover:bg-zinc-800 focus-visible:outline focus-visible:outline-2 focus-visible:outline-accent"
          data-testid="logout-button"
        >
          Выйти
        </button>
      </div>
    </div>
  );
}

export function Sidebar({ session, vehicleCount, activeHref = "/dashboard" }: SidebarProps) {
  const [open, setOpen] = useState(false);

  useEffect(() => {
    if (!open) return;
    function onKey(e: KeyboardEvent) {
      if (e.key === "Escape") setOpen(false);
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open]);

  useEffect(() => {
    document.body.style.overflow = open ? "hidden" : "";
    return () => {
      document.body.style.overflow = "";
    };
  }, [open]);

  return (
    <>
      {/* Desktop sidebar */}
      <aside className="hidden h-screen w-64 shrink-0 md:flex">
        <SidebarChrome session={session} vehicleCount={vehicleCount} activeHref={activeHref} />
      </aside>

      {/* Mobile top bar trigger lives as floating button */}
      <button
        type="button"
        onClick={() => setOpen(true)}
        className="fixed bottom-4 left-4 z-40 flex h-12 w-12 items-center justify-center rounded-full bg-accent text-sm font-bold text-white shadow-lg focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent md:hidden"
        aria-label="Открыть меню"
        aria-expanded={open}
      >
        Меню
      </button>

      {open ? (
        <div className="fixed inset-0 z-50 md:hidden" role="dialog" aria-modal="true" aria-label="Навигация">
          <button
            type="button"
            className="absolute inset-0 bg-black/50"
            aria-label="Закрыть меню"
            onClick={() => setOpen(false)}
          />
          <div className="absolute inset-y-0 left-0 shadow-xl">
            <SidebarChrome
              session={session}
              vehicleCount={vehicleCount}
              activeHref={activeHref}
              onNavigate={() => setOpen(false)}
              onClose={() => setOpen(false)}
            />
          </div>
        </div>
      ) : null}
    </>
  );
}
