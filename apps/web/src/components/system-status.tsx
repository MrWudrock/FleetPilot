import type { ReadinessResponse } from "@/lib/api";

type StatusBadgeProps = {
  label: string;
  status: string;
  detail?: string;
};

function StatusBadge({ label, status, detail }: StatusBadgeProps) {
  const ok = status === "ok";

  return (
    <div className="rounded-lg border border-zinc-200 bg-white px-4 py-3">
      <div className="flex items-center justify-between gap-3">
        <span className="text-sm font-medium text-zinc-700">{label}</span>
        <span
          className={`rounded-full px-2 py-0.5 text-xs font-semibold ${
            ok ? "bg-emerald-100 text-emerald-700" : "bg-red-100 text-red-700"
          }`}
        >
          {status}
        </span>
      </div>
      {detail ? <p className="mt-2 truncate text-xs text-zinc-500">{detail}</p> : null}
    </div>
  );
}

export function SystemStatus({ readiness }: { readiness: ReadinessResponse | null }) {
  if (!readiness) {
    return (
      <div className="rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
        API недоступен. Проверьте интернет и URL сервера в Настройках, либо обратитесь к администратору.
      </div>
    );
  }

  return (
    <div className="grid gap-3 md:grid-cols-3">
      <StatusBadge label="API" status={readiness.status} detail={`v${readiness.version}`} />
      <StatusBadge
        label="PostgreSQL"
        status={readiness.checks.postgres.status}
        detail={readiness.checks.postgres.detail}
      />
      <StatusBadge
        label="Redis"
        status={readiness.checks.redis.status}
        detail={readiness.checks.redis.detail}
      />
    </div>
  );
}
