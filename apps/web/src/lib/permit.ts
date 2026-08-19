import { getToken } from "@/lib/auth";
import { getApiBase } from "@/lib/config";

export type RoutePoint = {
  name?: string | null;
  address?: string | null;
  lat?: number | null;
  lon?: number | null;
};

export type CargoSpec = {
  length_m: number;
  width_m: number;
  height_m: number;
  mass_kg: number;
  axle_loads_kg: number[];
};

export type PermitAnalysis = {
  permit_required: boolean;
  podd_required: boolean;
  risk_level: string;
  risk_score: number;
  route_summary: string;
  restrictions: string[];
  special_conditions: string[];
  alternative_routes: string[];
  legal_references: string[];
  dispatcher_actions: string[];
  confidence: number;
};

export type PermitRequest = {
  id: string;
  status: string;
  origin: RoutePoint;
  destination: RoutePoint;
  cargo: CargoSpec;
  analysis: PermitAnalysis | null;
  risk_score: number | null;
  external_permit_number: string | null;
  dispatcher_notes: string | null;
  created_at: string;
};

function authHeaders(): HeadersInit {
  const token = getToken();
  if (!token) throw new Error("Не авторизован — войдите снова");
  return {
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/json",
  };
}

async function readError(response: Response, fallback: string): Promise<string> {
  const body = await response.json().catch(() => ({}));
  if (typeof body.detail === "string") return body.detail;
  if (Array.isArray(body.detail)) {
    return body.detail.map((d: { msg?: string }) => d.msg ?? String(d)).join(", ");
  }
  return fallback;
}

export async function analyzeRoute(payload: {
  origin: RoutePoint;
  destination: RoutePoint;
  cargo: CargoSpec;
  persist?: boolean;
}): Promise<{ analysis: PermitAnalysis; permit_request_id: string | null }> {
  const response = await fetch(`${getApiBase()}/api/v1/agents/permit/analyze-route`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify({ ...payload, persist: payload.persist ?? true }),
  });
  if (!response.ok) throw new Error(await readError(response, "Ошибка анализа маршрута"));
  return response.json();
}

export async function listPermitRequests(): Promise<{ items: PermitRequest[]; total: number }> {
  const response = await fetch(`${getApiBase()}/api/v1/agents/permit/requests`, {
    headers: authHeaders(),
  });
  if (!response.ok) throw new Error(await readError(response, "Не удалось загрузить заявки"));
  return response.json();
}

export async function approvePermitRequest(
  id: string,
  payload: { notes?: string; external_permit_number?: string },
): Promise<PermitRequest> {
  const response = await fetch(`${getApiBase()}/api/v1/agents/permit/requests/${id}/approve`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify(payload),
  });
  if (!response.ok) throw new Error(await readError(response, "Ошибка утверждения"));
  return response.json();
}

export async function checkRosdorPermit(payload: {
  permit_number: string;
  plate: string;
}): Promise<{
  found: boolean;
  permit_number: string;
  plate: string;
  status: string | null;
  valid_until: string | null;
  route_summary: string | null;
  source: string;
}> {
  const response = await fetch(`${getApiBase()}/api/v1/integrations/rosdor/permits/check`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify(payload),
  });
  if (!response.ok) throw new Error(await readError(response, "Ошибка проверки реестра"));
  return response.json();
}

export async function fetchRosdorHealth(): Promise<{
  status: string;
  message: string;
  configured: boolean;
}> {
  const response = await fetch(`${getApiBase()}/api/v1/integrations/rosdor/health`);
  if (!response.ok) throw new Error("Rosdor health failed");
  return response.json();
}
