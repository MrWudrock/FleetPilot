import { getToken } from "@/lib/auth";
import { getApiBase } from "@/lib/config";

function authHeaders(): HeadersInit {
  const token = getToken();
  if (!token) throw new Error("Не авторизован");
  return { Authorization: `Bearer ${token}`, "Content-Type": "application/json" };
}

async function readError(response: Response, fallback: string): Promise<string> {
  const body = await response.json().catch(() => ({}));
  if (typeof body.detail === "string") return body.detail;
  return fallback;
}

export type Vehicle = {
  id: string;
  plate: string;
  brand: string | null;
  model: string | null;
  capacity_kg: number | null;
  status: string;
  motion: string;
  position: {
    lat: number;
    lon: number;
    speed_kmh: number;
    ignition?: boolean;
    updated_at?: string;
    source?: string;
  } | null;
};

export type FuelAlert = {
  id: string;
  vehicle_id: string | null;
  plate: string | null;
  severity: string;
  title: string;
  detected_at: string;
  acknowledged: boolean;
};

export type Integration = {
  id: string;
  provider: string;
  status: string;
  last_sync_at: string | null;
  last_error: string | null;
  demo: boolean;
  label: string;
};

export type Order = {
  id: string;
  external_ref: string | null;
  status: string;
  details: {
    origin?: { name?: string };
    destination?: { name?: string };
    cargo?: { mass_kg?: number; description?: string };
    plate?: string;
    vehicle_id?: string | null;
    notes?: string;
  };
  created_at: string;
};

export async function fetchVehicles(): Promise<{ items: Vehicle[]; total: number }> {
  const res = await fetch(`${getApiBase()}/api/v1/vehicles`, { headers: authHeaders() });
  if (!res.ok) throw new Error(await readError(res, "Ошибка загрузки ТС"));
  return res.json();
}

export async function fetchFuelAlerts(): Promise<{
  items: FuelAlert[];
  total: number;
  unacknowledged: number;
}> {
  const res = await fetch(`${getApiBase()}/api/v1/fuel/alerts`, { headers: authHeaders() });
  if (!res.ok) throw new Error(await readError(res, "Ошибка алертов"));
  return res.json();
}

export async function acknowledgeFuelAlert(id: string): Promise<FuelAlert> {
  const res = await fetch(`${getApiBase()}/api/v1/fuel/alerts/${id}/acknowledge`, {
    method: "POST",
    headers: authHeaders(),
  });
  if (!res.ok) throw new Error(await readError(res, "Не удалось подтвердить"));
  return res.json();
}

export async function fetchIntegrations(): Promise<{ items: Integration[] }> {
  const res = await fetch(`${getApiBase()}/api/v1/integrations`, { headers: authHeaders() });
  if (!res.ok) throw new Error(await readError(res, "Ошибка интеграций"));
  return res.json();
}

export async function connectWialon(
  token: string,
  host = "https://wialon.local",
  demo = true,
): Promise<Integration> {
  const res = await fetch(`${getApiBase()}/api/v1/integrations/wialon/connect`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify({ token, host, demo }),
  });
  if (!res.ok) throw new Error(await readError(res, "Ошибка подключения Wialon"));
  return res.json();
}

export async function syncWialon(): Promise<{ synced: number; message: string }> {
  const res = await fetch(`${getApiBase()}/api/v1/integrations/wialon/sync`, {
    method: "POST",
    headers: authHeaders(),
  });
  if (!res.ok) throw new Error(await readError(res, "Ошибка sync Wialon"));
  return res.json();
}

export async function connectTransManager(token: string, demo = true): Promise<Integration> {
  const res = await fetch(`${getApiBase()}/api/v1/integrations/transmanager/connect`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify({ token, demo }),
  });
  if (!res.ok) throw new Error(await readError(res, "Ошибка подключения ТМ"));
  return res.json();
}

export async function syncTransManager(): Promise<{ synced: number; message: string }> {
  const res = await fetch(`${getApiBase()}/api/v1/integrations/transmanager/sync`, {
    method: "POST",
    headers: authHeaders(),
  });
  if (!res.ok) throw new Error(await readError(res, "Ошибка sync ТМ"));
  return res.json();
}

export async function fetchOrders(): Promise<{ items: Order[]; total: number }> {
  const res = await fetch(`${getApiBase()}/api/v1/orders`, { headers: authHeaders() });
  if (!res.ok) throw new Error(await readError(res, "Ошибка заявок"));
  return res.json();
}

export async function createOrder(payload: {
  origin_name: string;
  destination_name: string;
  mass_kg: number;
  length_m: number;
  width_m: number;
  height_m: number;
  notes?: string;
}): Promise<Order> {
  const res = await fetch(`${getApiBase()}/api/v1/orders`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(await readError(res, "Ошибка создания заявки"));
  return res.json();
}

export async function assignOrder(orderId: string, vehicleId: string): Promise<Order> {
  const res = await fetch(`${getApiBase()}/api/v1/orders/${orderId}/assign`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify({ vehicle_id: vehicleId }),
  });
  if (!res.ok) throw new Error(await readError(res, "Ошибка назначения"));
  return res.json();
}

export type RouteVariant = {
  id: string;
  label: string;
  distance_km: number;
  duration_h: number;
  fuel_cost_rub: number;
  savings_rub: number;
  via: string[];
};

export type RoutePlan = {
  order_id: string;
  external_ref: string | null;
  status: string;
  origin: string;
  destination: string;
  plate: string | null;
  recommended: string | null;
  accepted_variant_id: string | null;
  variants: RouteVariant[];
};

export type MaintenanceTask = {
  id: string;
  vehicle_id: string | null;
  plate: string | null;
  title: string;
  kind: string;
  status: string;
  due_at: string | null;
  mileage_km: number | null;
  estimated_cost_rub: number | null;
  notes: string | null;
  created_at: string;
};

export type OrgSettings = {
  timezone: string;
  currency: string;
  notify_fuel_email: boolean;
  notify_maintenance_days: number;
  demo_mode: boolean;
  default_origin: string;
};

export type SettingsPayload = {
  organization_id: string;
  name: string;
  slug: string;
  settings: OrgSettings;
};

export async function fetchRoutes(): Promise<{ items: RoutePlan[]; total: number }> {
  const res = await fetch(`${getApiBase()}/api/v1/routes`, { headers: authHeaders() });
  if (!res.ok) throw new Error(await readError(res, "Ошибка маршрутов"));
  return res.json();
}

export async function optimizeRoute(orderId: string): Promise<RoutePlan> {
  const res = await fetch(`${getApiBase()}/api/v1/routes/optimize`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify({ order_id: orderId }),
  });
  if (!res.ok) throw new Error(await readError(res, "Ошибка оптимизации"));
  return res.json();
}

export async function acceptRoute(orderId: string, variantId: string): Promise<RoutePlan> {
  const res = await fetch(`${getApiBase()}/api/v1/routes/${orderId}/accept`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify({ variant_id: variantId }),
  });
  if (!res.ok) throw new Error(await readError(res, "Ошибка принятия маршрута"));
  return res.json();
}

export async function fetchMaintenanceTasks(): Promise<{
  items: MaintenanceTask[];
  total: number;
  overdue: number;
}> {
  const res = await fetch(`${getApiBase()}/api/v1/maintenance/tasks`, { headers: authHeaders() });
  if (!res.ok) throw new Error(await readError(res, "Ошибка ТО"));
  return res.json();
}

export async function createMaintenanceTask(payload: {
  vehicle_id?: string;
  title: string;
  kind: string;
  due_at?: string;
  mileage_km?: number;
  estimated_cost_rub?: number;
  notes?: string;
}): Promise<MaintenanceTask> {
  const res = await fetch(`${getApiBase()}/api/v1/maintenance/tasks`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(await readError(res, "Ошибка создания задачи"));
  return res.json();
}

export async function startMaintenanceTask(id: string): Promise<MaintenanceTask> {
  const res = await fetch(`${getApiBase()}/api/v1/maintenance/tasks/${id}/start`, {
    method: "POST",
    headers: authHeaders(),
  });
  if (!res.ok) throw new Error(await readError(res, "Ошибка старта"));
  return res.json();
}

export async function completeMaintenanceTask(id: string): Promise<MaintenanceTask> {
  const res = await fetch(`${getApiBase()}/api/v1/maintenance/tasks/${id}/complete`, {
    method: "POST",
    headers: authHeaders(),
  });
  if (!res.ok) throw new Error(await readError(res, "Ошибка завершения"));
  return res.json();
}

export async function fetchSettings(): Promise<SettingsPayload> {
  const res = await fetch(`${getApiBase()}/api/v1/settings`, { headers: authHeaders() });
  if (!res.ok) throw new Error(await readError(res, "Ошибка настроек"));
  return res.json();
}

export async function updateSettings(payload: {
  name?: string;
  settings?: OrgSettings;
}): Promise<SettingsPayload> {
  const res = await fetch(`${getApiBase()}/api/v1/settings`, {
    method: "PATCH",
    headers: authHeaders(),
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(await readError(res, "Ошибка сохранения"));
  return res.json();
}
