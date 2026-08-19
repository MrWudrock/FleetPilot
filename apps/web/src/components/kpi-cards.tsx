import type { RoiKpi } from "@/lib/analytics";
import { formatRub } from "@/lib/analytics";

type KpiCardProps = {
  label: string;
  value: string;
  delta?: string;
  deltaPositive?: boolean;
};

function KpiCard({ label, value, delta, deltaPositive }: KpiCardProps) {
  return (
    <div className="rounded-lg border border-zinc-200 bg-white p-5 shadow-sm">
      <p className="text-xs font-medium uppercase tracking-wide text-zinc-500">{label}</p>
      <p className="mt-2 text-3xl font-extrabold text-zinc-800">{value}</p>
      {delta ? (
        <p
          className={`mt-1 text-xs font-semibold ${
            deltaPositive ? "text-emerald-600" : deltaPositive === false ? "text-red-600" : "text-zinc-400"
          }`}
        >
          {delta}
        </p>
      ) : null}
    </div>
  );
}

type KpiCardsProps = {
  kpi: RoiKpi | null;
  loading?: boolean;
};

export function KpiCards({ kpi, loading }: KpiCardsProps) {
  if (loading || !kpi) {
    return (
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
        {Array.from({ length: 5 }).map((_, index) => (
          <div
            key={index}
            className="h-28 animate-pulse rounded-lg border border-zinc-200 bg-white p-5"
          />
        ))}
      </div>
    );
  }

  const savingsDelta =
    kpi.monthly_savings_delta_pct !== null
      ? `${kpi.monthly_savings_delta_pct > 0 ? "↑" : "↓"} ${Math.abs(kpi.monthly_savings_delta_pct)}% vs прошлый мес.`
      : kpi.monthly_savings_rub > 0
        ? "Первый месяц с данными"
      : "Нет данных — подключите интеграции";

  const fuelDelta =
    kpi.fuel_alerts_critical > 0
      ? `${kpi.fuel_alerts_critical} критический`
      : kpi.fuel_alerts_count > 0
        ? "Требуют проверки"
        : "Нет активных алертов";

  const roiValue =
    kpi.roi_percent_annual !== null ? `${kpi.roi_percent_annual}%` : "—";

  const roiDelta =
    kpi.payback_months !== null
      ? `Окупаемость ${kpi.payback_months} мес.`
      : "Нужны данные экономии";

  const cards: KpiCardProps[] = [
    {
      label: "Экономия за месяц",
      value: formatRub(kpi.monthly_savings_rub),
      delta: savingsDelta,
      deltaPositive: (kpi.monthly_savings_delta_pct ?? 0) > 0,
    },
    {
      label: "ТС в автопарке",
      value: String(kpi.vehicle_count),
      delta: `${kpi.active_vehicle_count} активных`,
      deltaPositive: kpi.active_vehicle_count > 0,
    },
    {
      label: "Активных маршрутов",
      value: String(kpi.active_routes_count),
      delta: `${kpi.orders_today} заявок сегодня`,
      deltaPositive: kpi.active_routes_count > 0,
    },
    {
      label: "Топливные алерты",
      value: String(kpi.fuel_alerts_count),
      delta: fuelDelta,
      deltaPositive: kpi.fuel_alerts_count === 0,
    },
    {
      label: "ROI за 12 мес.",
      value: roiValue,
      delta: roiDelta,
      deltaPositive: (kpi.roi_percent_annual ?? 0) >= 100,
    },
  ];

  return (
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
      {cards.map((card) => (
        <KpiCard key={card.label} {...card} />
      ))}
    </div>
  );
}
