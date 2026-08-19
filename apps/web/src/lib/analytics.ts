import { getToken } from "@/lib/auth";
import { getApiBase } from "@/lib/config";

export type RoiKpi = {
  monthly_savings_rub: number;
  monthly_savings_delta_pct: number | null;
  vehicle_count: number;
  active_vehicle_count: number;
  active_routes_count: number;
  orders_today: number;
  fuel_alerts_count: number;
  fuel_alerts_critical: number;
  roi_percent_annual: number | null;
  payback_months: number | null;
  annual_savings_rub: number;
  subscription_cost_monthly_rub: number;
  breakdown: {
    fuel: number;
    route: number;
    dispatch: number;
    maintenance: number;
  };
};

export async function fetchRoiKpi(): Promise<RoiKpi> {
  const token = getToken();
  if (!token) throw new Error("Not authenticated");

  const response = await fetch(`${getApiBase()}/api/v1/analytics/roi`, {
    headers: { Authorization: `Bearer ${token}` },
  });

  if (!response.ok) {
    throw new Error("Failed to load KPI data");
  }

  return response.json();
}

export function formatRub(value: number): string {
  return new Intl.NumberFormat("ru-RU", {
    style: "currency",
    currency: "RUB",
    maximumFractionDigits: 0,
  }).format(value);
}
